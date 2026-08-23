import pandas as pd
import matplotlib.pyplot as plt
import os
from typing import Dict

class EDAAgent:
    """
    Performs exploratory data analysis 
    and store results in structured format."""

    def run(self,dataset_path: str, target_column: str)-> Dict:
        df=pd.read_csv(dataset_path)

        #--- basic Statistics---
        numeric_summary= df.describe().to_dict()
        #--- Missing values------
        missing_values= df.isnull().sum().to_dict()
        #---- Target distribution ----
        target_distribution=df[target_column].value_counts().to_dict()

        #-----Plot directory-----
        plot_dir="artifacts/eda_plots"
        os.makedirs(plot_dir, exist_ok=True)

        #-----Plot:target distribution----
        plt.figure()
        df[target_column].value_counts().plot(kind='bar')
        plt.title(f"target Distribution: {target_column}")
        plt.xlabel(target_column)
        plt.ylabel("Count")
        plt.tight_layout()

        plot_path=os.path.join(plot_dir, "target_distribution.png")
        plt.savefig(plot_path)
        plt.close()

        return{
            "eda_summary":{
                "numeric_summary": numeric_summary,
                "missing_values": missing_values,
                "target_distribution": target_distribution
            },
            "eda_plots_path": plot_path
        }

