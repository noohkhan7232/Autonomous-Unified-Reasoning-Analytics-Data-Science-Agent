import pandas as pd
from agents.planner import PlannerAgent
from agents.eda import EDAAgent
from state import AnalysisState
from typing import Dict
import matplotlib.pyplot as plt
# planner = PlannerAgent()
# state= AnalysisState(dataset_path="data/raw/adult.csv")
# result = planner.run(state.dataset_path)
# state.dataset_summary = result["dataset_summary"]
# state.plan = result["plan"]
# state.task_type = result["plan"]["task_type"]
# state.target_column = result["plan"]["target_column"]

# eda_agent = EDAAgent()
# eda_result = eda_agent.run(dataset_path= state.dataset_path,
#                            target_column= state.target_column)
# print(eda_result)
#print(result)
# df=pd.read_csv("data/raw/adult.csv")
# print(df.drop(columns=["income"]))
# print(df["income"])
# print(df.columns[-1])
# print(df["income"].value_counts().to_dict())
# plt.figure()
# df["income"].value_counts().plot(kind='bar')
# plt.show()

# summary={
#             "num_rows": df.shape[0],
#             "num_columns": df.shape[1],
#             "columns": df.columns.tolist(),
#             "dtypes": df.dtypes.apply(lambda x: x.name).to_dict(),
#             "missing_values": df.isnull().sum().to_dict()
#         }
#print(df.shape)
#print(f"row: {df.shape[0]}")
#print(f"columns: {df.shape[1]}")
#print(df.columns[0])
#print(df.dtypes.apply(lambda x: x.name).to_dict())
#print(df.isnull().sum().to_dict())
# target_column=df.columns[-1]
# print(target_column)
# print(df[target_column].nunique())
        # if df[target_column].nunique()<=10:
        #     task_type="classification"
        # else:
        #     task_type="regression"
        # plan = {
        #     "task_type": task_type,
        #     "target_column": target_column,
        #     "steps": ["Exploratory_data_analysis",
        #               "feature_engineering",
        #               "model_training", 
        #               "evaluation"
        #               ]
        # }
        # return {
        #     "dataset_summary": summary,
        #     "task_type": task_type,
        #     "target_column": target_column,
        #     "plan": plan
        # }
class Dog:
    def bark(response):
        return response
print(Dog.bark("Bark"))   
Dog()