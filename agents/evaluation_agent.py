from typing import Any, Dict, List


class EvaluationAgent:
    """
    Evaluates the quality of the autonomous data science pipeline.

    Produces:
    - data quality score
    - model quality score
    - overall system score
    - issues
    - actionable recommendations
    - pass/fail verdict
    """

    DATA_WEIGHT = 0.4
    MODEL_WEIGHT = 0.6
    PASS_THRESHOLD = 0.7

    def __init__(self):
        pass

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate pipeline outputs and return a structured evaluation result.
        """

        issues: List[str] = []
        recommendations: List[str] = []

        data_score = self.evaluate_data_quality(
            state,
            issues,
            recommendations,
        )

        model_score = self.evaluate_model_quality(
            state,
            issues,
            recommendations,
        )

        system_score = round(
            self.DATA_WEIGHT * data_score
            + self.MODEL_WEIGHT * model_score,
            3,
        )

        verdict = (
            "PASS"
            if system_score >= self.PASS_THRESHOLD
            else "FAIL"
        )

        return {
            "data_quality_score": data_score,
            "model_quality_score": model_score,
            "system_score": system_score,
            "verdict": verdict,
            "issues": issues,
            "recommendations": recommendations,
            "requires_retraining": verdict == "FAIL",
        }

    # ------------------------------------------------------------------
    # DATA QUALITY
    # ------------------------------------------------------------------

    def evaluate_data_quality(
        self,
        state: Dict[str, Any],
        issues: List[str],
        recommendations: List[str],
    ) -> float:

        eda = state.get("eda_summary", {})

        missing_values = eda.get("missing_values", {})

        total_missing = sum(
            value
            for value in missing_values.values()
            if isinstance(value, (int, float))
        )

        if total_missing > 0:
            issues.append(
                f"Dataset contains {total_missing} missing values."
            )

            recommendations.append(
                "Review missing-value handling before model retraining."
            )

        # Support both current EDA naming and future naming.
        distribution = eda.get(
            "target_distribution",
            eda.get("class_distribution"),
        )

        imbalance_ratio = None

        if isinstance(distribution, dict) and distribution:

            numeric_counts = [
                value
                for value in distribution.values()
                if isinstance(value, (int, float))
            ]

            total_samples = sum(numeric_counts)

            if total_samples > 0:
                imbalance_ratio = max(numeric_counts) / total_samples

                if imbalance_ratio > 0.85:
                    issues.append(
                        "Severe target class imbalance detected."
                    )

                    recommendations.append(
                        "Consider class weighting, resampling, "
                        "or imbalance-aware evaluation metrics."
                    )

        score = 1.0

        if total_missing > 0:
            score -= 0.3

        if imbalance_ratio is not None and imbalance_ratio > 0.85:
            score -= 0.3

        return round(max(0.0, score), 3)

    # ------------------------------------------------------------------
    # MODEL QUALITY
    # ------------------------------------------------------------------

    def evaluate_model_quality(
        self,
        state: Dict[str, Any],
        issues: List[str],
        recommendations: List[str],
    ) -> float:

        metrics = state.get("model_metrics", {})

        if not isinstance(metrics, dict) or not metrics:
            issues.append("No model evaluation metrics were provided.")

            recommendations.append(
                "Run model evaluation before generating the final report."
            )

            return 0.0

        # Classification
        if "accuracy" in metrics:

            accuracy = float(metrics["accuracy"])

            if accuracy < 0.70:
                issues.append(
                    f"Low classification accuracy: {accuracy:.3f}"
                )

                recommendations.append(
                    "Try alternative classification algorithms "
                    "or perform additional feature engineering."
                )

            elif accuracy < 0.80:
                issues.append(
                    f"Moderate classification accuracy: {accuracy:.3f}"
                )

                recommendations.append(
                    "Benchmark the current model against additional "
                    "classification algorithms."
                )

            return round(min(1.0, max(0.0, accuracy)), 3)

        # Regression
        if "rmse" in metrics:

            rmse = float(metrics["rmse"])

            if rmse > 10:
                issues.append(
                    f"High regression RMSE: {rmse:.3f}"
                )

                recommendations.append(
                    "Consider feature engineering, model tuning, "
                    "or alternative regression algorithms."
                )

            return round(
                max(0.0, 1 - rmse / 100),
                3,
            )

        issues.append(
            "Unknown or unsupported model evaluation metric."
        )

        recommendations.append(
            "Add a supported evaluation metric for the selected task."
        )

        return 0.0