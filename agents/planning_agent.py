import pandas as pd
from typing import Dict

class PlannerAgent:
    """
    Decides what kind of data science task this is and produce a structured analysis plan.

    """
    def run(self, dataset_path:str)-> Dict:
        df=pd.read_csv(dataset_path)
        summary={
            "num_rows": df.shape[0],
            "num_columns": df.shape[1],
            "columns": df.columns.tolist(),
            "dtypes": df.dtypes.apply(lambda x: x.name).to_dict(),
            "missing_values": df.isnull().sum().to_dict()
        }
        target_column=df.columns[-1]
        if df[target_column].nunique()<=10:
            task_type="classification"
        else:
            task_type="regression"
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
   