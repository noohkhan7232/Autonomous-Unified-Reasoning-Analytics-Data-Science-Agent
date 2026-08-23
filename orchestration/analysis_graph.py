from langgraph.graph import StateGraph, END

from agents.planning_agent import PlannerAgent
from agents.exploratory_analysis_agent import EDAAgent
from agents.modeling_agent import ModelingAgent
from agents.explanation_agent import ExplanationAgent
from agents.evaluation_agent import EvaluationAgent


# ============================================================
# PLANNING NODE
# ============================================================

def planner_node(state: dict) -> dict:
    planner = PlannerAgent()

    result = planner.run(
        state["dataset_path"]
    )

    return {
        **state,
        "dataset_summary": result["dataset_summary"],
        "task_type": result["task_type"],
        "target_column": result["target_column"],
        "plan": result["plan"],
        "current_agent": "planner",
        "execution_status": "planning_completed",
    }


# ============================================================
# EDA NODE
# ============================================================

def eda_node(state: dict) -> dict:
    eda_agent = EDAAgent()

    result = eda_agent.run(
        dataset_path=state["dataset_path"],
        target_column=state["target_column"],
    )

    return {
        **state,
        "eda_summary": result["eda_summary"],
        "eda_plots_path": result["eda_plots_path"],
        "current_agent": "eda",
        "execution_status": "eda_completed",
    }


# ============================================================
# MODELING NODE
# ============================================================

def modeling_node(state: dict) -> dict:
    modeling_agent = ModelingAgent()

    result = modeling_agent.run(
        dataset_path=state["dataset_path"],
        target_column=state["target_column"],
        task_type=state["task_type"],
    )

    return {
        **state,
        "model_type": result["model_type"],
        "model_metrics": result["model_metrics"],
        "model_artifact_path": result["model_artifact_path"],

        "model_comparison": result["model_comparison"],
"best_model": result["best_model"],



        "current_agent": "modeling",
        "execution_status": "modeling_completed",
    }


# ============================================================
# EVALUATION NODE
# ============================================================

def evaluation_node(state: dict) -> dict:
    evaluator = EvaluationAgent()

    evaluation = evaluator.run(state)

    # Extract pass/fail safely
    evaluation_passed = evaluation.get(
        "evaluation_passed",
        evaluation.get("verdict", "").upper() == "PASS"
    )

    return {
        **state,
        "evaluation_summary": evaluation,
        "evaluation_passed": evaluation_passed,
        "current_agent": "evaluation",
        "execution_status": "evaluation_completed",
    }


# ============================================================
# SELF-CORRECTION NODE
# ============================================================

def self_correction_node(state: dict) -> dict:

    retry_count = state.get("retry_count", 0) + 1

    evaluation = state.get("evaluation_summary", {})

    reason = (
        evaluation.get("correction_reason")
        or evaluation.get("reason")
        or "Model or system quality below acceptance threshold."
    )

    return {
        **state,
        "retry_count": retry_count,
        "self_correction_triggered": True,
        "correction_reason": reason,
        "decision": "RETRY",
        "execution_status": "self_correction_triggered",
        "current_agent": "self_correction",
    }


# ============================================================
# DECISION ROUTER
# ============================================================

def decision_router(state: dict) -> str:

    evaluation_passed = state.get(
        "evaluation_passed",
        False
    )

    retry_count = state.get(
        "retry_count",
        0
    )

    max_retries = state.get(
        "max_retries",
        2
    )

    # --------------------------------------------------------
    # PASS
    # --------------------------------------------------------

    if evaluation_passed:
        return "explanation"

    # --------------------------------------------------------
    # FAIL + RETRY AVAILABLE
    # --------------------------------------------------------

    if retry_count < max_retries:
        return "self_correction"

    # --------------------------------------------------------
    # FAIL + RETRIES EXHAUSTED
    # --------------------------------------------------------

    return "explanation"


# ============================================================
# EXPLANATION NODE
# ============================================================

def explanation_node(state: dict) -> dict:

    explanation_agent = ExplanationAgent()

    final_report = explanation_agent.run(
        eda_summary=state["eda_summary"],
        model_metrics=state["model_metrics"],
        task_type=state["task_type"],
        target_column=state["target_column"],
    )

    return {
        **state,
        "final_report": final_report,
        "current_agent": "explanation",
        "execution_status": "completed",
    }


# ============================================================
# GRAPH CONSTRUCTION
# ============================================================

graph = StateGraph(dict)


graph.add_node(
    "planner",
    planner_node
)

graph.add_node(
    "eda",
    eda_node
)

graph.add_node(
    "modeling",
    modeling_node
)

graph.add_node(
    "evaluation",
    evaluation_node
)

graph.add_node(
    "self_correction",
    self_correction_node
)

graph.add_node(
    "explanation",
    explanation_node
)


# ============================================================
# LINEAR FLOW
# ============================================================

graph.set_entry_point("planner")

graph.add_edge(
    "planner",
    "eda"
)

graph.add_edge(
    "eda",
    "modeling"
)

graph.add_edge(
    "modeling",
    "evaluation"
)


# ============================================================
# INTELLIGENT ROUTING
# ============================================================

graph.add_conditional_edges(
    "evaluation",
    decision_router,
    {
        "explanation": "explanation",
        "self_correction": "self_correction",
    },
)


# ============================================================
# SELF-CORRECTION LOOP
# ============================================================

graph.add_edge(
    "self_correction",
    "modeling"
)


# ============================================================
# FINAL OUTPUT
# ============================================================

graph.add_edge(
    "explanation",
    END
)


# ============================================================
# COMPILE
# ============================================================

app = graph.compile()


# ============================================================
# TEST EXECUTION
# ============================================================

if __name__ == "__main__":

    initial_state = {
        "dataset_path": "data/adult.csv",
        "retry_count": 0,
        "max_retries": 2,
        "self_correction_triggered": False,
        "execution_status": "initialized",
    }

    final_state = app.invoke(
        initial_state
    )

    print(
        "\n=== AUTONOMOUS GRAPH EXECUTION COMPLETED ==="
    )

    print(
        "\nDecision:",
        final_state.get("decision")
    )

    print(
        "Evaluation Passed:",
        final_state.get("evaluation_passed")
    )

    print(
        "Retry Count:",
        final_state.get("retry_count")
    )

    print(
        "Self Correction:",
        final_state.get("self_correction_triggered")
    )

    print(
        "\nEvaluation:"
    )

    print(
        final_state.get("evaluation_summary")
    )

    print(
        "\nFinal Report:"
    )

    print(
        final_state.get("final_report")
    )