from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class AnalysisState:
    """
    Shared execution state for the AURA-DS agentic data science pipeline.

    The state is passed between planning, EDA, modeling,
    evaluation, and explanation agents.
    """

    # ------------------------------------------------------------------
    # Input
    # ------------------------------------------------------------------
    dataset_path: str

    # ------------------------------------------------------------------
    # Execution metadata
    # ------------------------------------------------------------------
    current_agent: Optional[str] = None
    execution_status: str = "initialized"
    retry_count: int = 0

    # ------------------------------------------------------------------
    # Planner outputs
    # ------------------------------------------------------------------
    dataset_summary: Optional[Dict[str, Any]] = None
    task_type: Optional[str] = None
    target_column: Optional[str] = None

    plan: Dict[str, Any] = field(
        default_factory=lambda: {
            "steps": [
                "eda",
                "model",
                "evaluate",
                "explain",
            ]
        }
    )

    # ------------------------------------------------------------------
    # EDA outputs
    # ------------------------------------------------------------------
    eda_summary: Optional[Dict[str, Any]] = None
    eda_plots_path: Optional[str] = None

    # ------------------------------------------------------------------
    # Modeling outputs
    # ------------------------------------------------------------------
    model_type: Optional[str] = None
    model_metrics: Optional[Dict[str, Any]] = None
    model_artifact_path: Optional[str] = None

    # ------------------------------------------------------------------
    # Evaluation outputs
    # ------------------------------------------------------------------
    evaluation_summary: Optional[Dict[str, Any]] = None
    evaluation_passed: Optional[bool] = None

        # ------------------------------------------------------------------
    # Autonomous decision / self-correction
    # ------------------------------------------------------------------
    decision: Optional[str] = None
    correction_reason: Optional[str] = None
    max_retries: int = 2
    self_correction_triggered: bool = False


    # ------------------------------------------------------------------
    # Error handling
    # ------------------------------------------------------------------
    errors: Optional[str] = None
    validation_errors: List[str] = field(default_factory=list)

    # ------------------------------------------------------------------
    # Explanation / final outputs
    # ------------------------------------------------------------------
    final_report: Optional[str] = None