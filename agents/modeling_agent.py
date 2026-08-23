import os
import time
from typing import Dict, Any

import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


class ModelingAgent:
    """
    Multi-model benchmarking and intelligent model selection agent.

    The agent:
    1. Loads the dataset.
    2. Creates a leakage-safe preprocessing pipeline.
    3. Trains multiple candidate classification models.
    4. Evaluates every candidate using multiple metrics.
    5. Selects the best-performing model.
    6. Saves the winning model as an artifact.
    """

    def __init__(self):
        self.random_state = 42

    def run(
        self,
        dataset_path: str,
        target_column: str,
        task_type: str,
    ) -> Dict[str, Any]:

        # ============================================================
        # 1. LOAD DATA
        # ============================================================

        df = pd.read_csv(dataset_path)

        X = df.drop(columns=[target_column])
        y = df[target_column]

        # ============================================================
        # 2. TRAIN / TEST SPLIT
        # ============================================================

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.2,
            random_state=self.random_state,
            stratify=y if task_type == "classification" else None,
        )

        # ============================================================
        # 3. IDENTIFY FEATURE TYPES
        # ============================================================

        categorical_cols = X.select_dtypes(
            include=["object"]
        ).columns

        numeric_cols = X.select_dtypes(
            exclude=["object"]
        ).columns

        # ============================================================
        # 4. PREPROCESSING
        # ============================================================

        preprocessor = ColumnTransformer(
            transformers=[
                (
                    "cat",
                    OneHotEncoder(handle_unknown="ignore"),
                    categorical_cols,
                ),
                (
                    "num",
                    StandardScaler(),
                    numeric_cols,
                ),
            ]
        )

        # ============================================================
        # 5. MODEL CANDIDATES
        # ============================================================

        if task_type != "classification":
            raise NotImplementedError(
                "Phase 6 currently supports classification only."
            )

        candidates = {
            "logistic_regression": LogisticRegression(
                max_iter=1000,
                random_state=self.random_state,
            ),

            "random_forest": RandomForestClassifier(
                n_estimators=200,
                random_state=self.random_state,
                n_jobs=-1,
            ),

            "gradient_boosting": GradientBoostingClassifier(
                n_estimators=150,
                random_state=self.random_state,
            ),
        }

        # ============================================================
        # 6. BENCHMARK ALL MODELS
        # ============================================================

        benchmark_results = {}

        trained_pipelines = {}

        print("\n" + "=" * 60)
        print("              MODEL BENCHMARK")
        print("=" * 60)

        for model_name, model in candidates.items():

            print(
                f"\nTraining: {model_name}"
            )

            pipeline = Pipeline(
                steps=[
                    (
                        "preprocessing",
                        preprocessor,
                    ),
                    (
                        "model",
                        model,
                    ),
                ]
            )

            start_time = time.perf_counter()

            pipeline.fit(
                X_train,
                y_train,
            )

            training_time = (
                time.perf_counter()
                - start_time
            )

            y_pred = pipeline.predict(
                X_test
            )

            accuracy = accuracy_score(
                y_test,
                y_pred,
            )

            precision = precision_score(
                y_test,
                y_pred,
                average="weighted",
                zero_division=0,
            )

            recall = recall_score(
                y_test,
                y_pred,
                average="weighted",
                zero_division=0,
            )

            f1 = f1_score(
                y_test,
                y_pred,
                average="weighted",
                zero_division=0,
            )

            benchmark_results[model_name] = {
                "accuracy": round(
                    float(accuracy),
                    4,
                ),
                "precision": round(
                    float(precision),
                    4,
                ),
                "recall": round(
                    float(recall),
                    4,
                ),
                "f1": round(
                    float(f1),
                    4,
                ),
                "training_time_seconds": round(
                    float(training_time),
                    4,
                ),
            }

            trained_pipelines[
                model_name
            ] = pipeline

            print(
                f"Accuracy:  {accuracy:.4f}"
            )

            print(
                f"Precision: {precision:.4f}"
            )

            print(
                f"Recall:    {recall:.4f}"
            )

            print(
                f"F1 Score:  {f1:.4f}"
            )

            print(
                f"Training:  {training_time:.4f}s"
            )

        # ============================================================
        # 7. SELECT BEST MODEL
        # ============================================================

        best_model_type = max(
            benchmark_results,
            key=lambda name: (
                benchmark_results[name]["f1"],
                benchmark_results[name]["accuracy"],
            ),
        )

        best_metrics = benchmark_results[
            best_model_type
        ]

        best_pipeline = trained_pipelines[
            best_model_type
        ]

        print("\n" + "-" * 60)
        print(
            f"BEST MODEL: {best_model_type}"
        )
        print(
            f"Best F1: {best_metrics['f1']:.4f}"
        )
        print(
            f"Best Accuracy: "
            f"{best_metrics['accuracy']:.4f}"
        )
        print("-" * 60)

        # ============================================================
        # 8. SAVE BEST MODEL
        # ============================================================

        model_dir = "artifacts/models"

        os.makedirs(
            model_dir,
            exist_ok=True,
        )

        model_path = os.path.join(
            model_dir,
            "best_model.pkl",
        )

        joblib.dump(
            best_pipeline,
            model_path,
        )

        # ============================================================
        # 9. RETURN STRUCTURED RESULT
        # ============================================================

        return {
            "model_type": best_model_type,

            "model_metrics": best_metrics,

            "model_comparison": benchmark_results,

            "best_model": best_model_type,

            "model_artifact_path": model_path,
        }