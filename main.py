from dotenv import load_dotenv

load_dotenv()

from agents.planning_agent import PlannerAgent
from agents.exploratory_analysis_agent import EDAAgent
from agents.modeling_agent import ModelingAgent
from agents.evaluation_agent import EvaluationAgent
from agents.explanation_agent import ExplanationAgent

from core.analysis_state import AnalysisState


def main():

    print("\n" + "=" * 60)
    print("              AURA-DS EXECUTION")
    print("=" * 60)

    # ============================================================
    # 1. INITIALIZE STATE
    # ============================================================

    state = AnalysisState(
        dataset_path="data/adult.csv"
    )

    # ============================================================
    # 2. PLANNING
    # ============================================================

    print("\n[1/5] PLANNING")

    planner = PlannerAgent()

    result = planner.run(
        state.dataset_path
    )

    state.dataset_summary = result["dataset_summary"]
    state.plan = result["plan"]

    state.task_type = result["plan"]["task_type"]
    state.target_column = result["plan"]["target_column"]

    print("      ✓ Planning completed")
    print("      Task:", state.task_type)
    print("      Target:", state.target_column)

    # ============================================================
    # 3. EDA
    # ============================================================

    print("\n[2/5] EXPLORATORY DATA ANALYSIS")

    eda_agent = EDAAgent()

    eda_result = eda_agent.run(
        dataset_path=state.dataset_path,
        target_column=state.target_column
    )

    state.eda_summary = eda_result["eda_summary"]
    state.eda_plots_path = eda_result["eda_plots_path"]

    print("      ✓ EDA completed")
    print("      Summary:", list(state.eda_summary.keys()))
    print("      Plot:", state.eda_plots_path)

    # ============================================================
    # 4. MODELING
    # ============================================================

    print("\n[3/5] MODELING")

    modeling_agent = ModelingAgent()

    modeling_result = modeling_agent.run(
        dataset_path=state.dataset_path,
        target_column=state.target_column,
        task_type=state.task_type
    )

    state.model_type = modeling_result["model_type"]
    state.model_metrics = modeling_result["model_metrics"]
    state.model_artifact_path = modeling_result["model_artifact_path"]

    print("      ✓ Modeling completed")
    print("      Model:", state.model_type)
    print("      Metrics:", state.model_metrics)
    print("      Artifact:", state.model_artifact_path)

    # ============================================================
    # 5. EVALUATION
    # ============================================================

    print("\n[4/5] INTELLIGENT EVALUATION")

    evaluation_agent = EvaluationAgent()

    evaluation_input = {
        "eda_summary": state.eda_summary,
        "model_metrics": state.model_metrics,
        "task_type": state.task_type,
        "target_column": state.target_column,
        "model_type": state.model_type,
    }

    evaluation_result = evaluation_agent.run(
        evaluation_input
    )

    print("\n      Evaluation Results")
    print("      ----------------------------")

    print(
        "      Data Quality Score:",
        evaluation_result["data_quality_score"]
    )

    print(
        "      Model Quality Score:",
        evaluation_result["model_quality_score"]
    )

    print(
        "      System Score:",
        evaluation_result["system_score"]
    )

    print(
        "      Verdict:",
        evaluation_result["verdict"]
    )

    print(
        "      Retraining Required:",
        evaluation_result["requires_retraining"]
    )

    # Show detected issues
    if evaluation_result["issues"]:

        print("\n      Issues:")

        for issue in evaluation_result["issues"]:
            print("      -", issue)

    # Show recommendations
    if evaluation_result["recommendations"]:

        print("\n      Recommendations:")

        for recommendation in evaluation_result["recommendations"]:
            print("      -", recommendation)

    # ============================================================
    # 6. DECISION ROUTING
    # ============================================================

    if evaluation_result["verdict"] == "FAIL":

        print("\n      ✗ QUALITY CHECK FAILED")
        print("      Autonomous re-training is required.")

        print("\n" + "=" * 60)
        print("              PIPELINE STOPPED")
        print("=" * 60)

        return

    # ============================================================
    # 7. EXPLANATION
    # ============================================================

    print("\n[5/5] EXPLANATION")

    explanation_agent = ExplanationAgent()

    final_report = explanation_agent.run(
        eda_summary=state.eda_summary,
        model_metrics=state.model_metrics,
        task_type=state.task_type,
        target_column=state.target_column
    )

    state.final_report = final_report

    print("      ✓ Explanation generated")

    # ============================================================
    # 8. FINAL REPORT
    # ============================================================

    print("\n" + "=" * 60)
    print("                  FINAL REPORT")
    print("=" * 60)

    print(state.final_report)

    # ============================================================
    # 9. FINAL STATUS
    # ============================================================

    print("\n" + "=" * 60)
    print("              AURA-DS PIPELINE COMPLETE")
    print("=" * 60)

    print("\nSystem Score:", evaluation_result["system_score"])
    print("Verdict:", evaluation_result["verdict"])
    print("Model:", state.model_type)
    print("Accuracy:", state.model_metrics.get("accuracy", "N/A"))
    print("Model Artifact:", state.model_artifact_path)
    print("EDA Plot:", state.eda_plots_path)

    print("\n✓ Autonomous analysis completed successfully.")


if __name__ == "__main__":
    main()