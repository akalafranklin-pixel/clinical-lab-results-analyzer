import json
import pandas as pd
from typing import Dict


class LabAnalyzer:
    def __init__(self, reference_path: str):
        # Load reference ranges once when the analyzer is created
        with open(reference_path, "r") as file:
            self.reference_ranges = json.load(file)

    def analyze_test(
        self,
        panel: str,
        test_name: str,
        value: float,
        sex: str
    ) -> Dict:
        """
        Analyze a single lab test result.
        """

        # Try to locate the test inside the reference ranges
        try:
            test_info = self.reference_ranges[panel][test_name]
        except KeyError:
            raise ValueError(f"Test '{test_name}' not found in panel '{panel}'")

        # Get sex-specific reference range
        lower, upper = test_info["range"][sex.lower()]
        unit = test_info["unit"]

        # Determine status
        if value < lower:
            status = "Low"
        elif value > upper:
            status = "High"
        else:
            status = "Normal"

        return {
            "panel": panel,
            "test": test_name,
            "value": value,
            "unit": unit,
            "reference_range": f"{lower} – {upper}",
            "status": status
        }

    def analyze_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze an uploaded CSV/Excel dataframe row-by-row.

        Required columns:
        - test
        - value
        - sex

        Optional:
        - panel (defaults to 'General')
        """

        results = []

        # Loop through each row in the uploaded file
        for _, row in df.iterrows():

            # Use default panel if not provided
            panel = row.get("panel", "General")

            test = row["test"]
            value = row["value"]
            sex = row.get("sex", "male")

            # Analyze one test
            result = self.analyze_test(
                panel=panel,
                test_name=test,
                value=value,
                sex=sex
            )

            results.append(result)

        # Convert results into a DataFrame
        return pd.DataFrame(results)
