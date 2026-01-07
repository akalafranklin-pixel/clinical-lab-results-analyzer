import json
from typing import Dict


class LabAnalyzer:
    def __init__(self, reference_path: str):
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

        try:
            test_info = self.reference_ranges[panel][test_name]
        except KeyError:
            raise ValueError(f"Test '{test_name}' not found in panel '{panel}'")

        lower, upper = test_info["range"][sex.lower()]
        unit = test_info["unit"]

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
