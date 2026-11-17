import pandas as pd
from typing import Dict

class PlannerAgent:
    """
    Decides what kind of data science task this is and produce a structured analysis plan.

    """
    def run(self, dataset_path:str, target_column=None, task_type=None)-> Dict:
        df=pd.read_csv(dataset_path)
        summary={
            "num_rows": df.shape[0],
            "num_columns": df.shape[1],
            "columns": df.columns.tolist(),
            "dtypes": df.dtypes.apply(lambda x: x.name).to_dict(),
            "missing_values": df.isnull().sum().to_dict()
        }
        target_column = target_column if target_column is not None else df.columns[-1]
        if task_type is None:
            task_type = "classification" if df[target_column].nunique() <= 10 else "regression"
        plan = {
            "task_type": task_type,
            "target_column": target_column,
            "steps": ["Exploratory_data_analysis",
                      "feature_engineering",
                      "model_training", 
                      "evaluation"
                      ]
        }
        return {
            "dataset_summary": summary,
            "task_type": task_type,
            "target_column": target_column,
            "plan": plan
        }
   
