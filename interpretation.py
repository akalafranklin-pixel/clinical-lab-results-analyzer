from typing import List, Dict


class ClinicalInterpreter:
    def __init__(self, analyzed_results: List[Dict]):
        """
        analyzed_results: list of dictionaries returned by LabAnalyzer
        """
        self.results = analyzed_results
        self.result_map = {r["test"]: r for r in analyzed_results}

    def interpret(self) -> List[str]:
        insights = []

        insights.extend(self._infection_pattern())
        insights.extend(self._anemia_pattern())
        insights.extend(self._renal_pattern())

        if not insights:
            insights.append(
                "No significant abnormal lab patterns detected based on available data."
            )

        return insights

    # ------------------ Pattern Rules ------------------ #

    def _infection_pattern(self) -> List[str]:
        insights = []

        wbc = self.result_map.get("WBC")
        neut = self.result_map.get("Neutrophils")

        if wbc and neut:
            if wbc["status"] == "High" and neut["status"] == "High":
                insights.append(
                    "Elevated white blood cells with neutrophilia may be consistent with an acute bacterial infection."
                )

        return insights

    def _anemia_pattern(self) -> List[str]:
        insights = []

        hb = self.result_map.get("Hemoglobin")
        rbc = self.result_map.get("RBC")
        hct = self.result_map.get("Hematocrit")

        low_count = sum(
            test and test["status"] == "Low"
            for test in [hb, rbc, hct]
        )

        if low_count >= 2:
            insights.append(
                "Reduced hemoglobin, red blood cells, and/or hematocrit values are consistent with anemia."
            )

        return insights

    def _renal_pattern(self) -> List[str]:
        insights = []

        urea = self.result_map.get("Urea")
        creat = self.result_map.get("Creatinine")

        if urea and creat:
            if urea["status"] == "High" and creat["status"] == "High":
                insights.append(
                    "Concurrent elevation of urea and creatinine may indicate impaired renal function."
                )

        return insights
    
 