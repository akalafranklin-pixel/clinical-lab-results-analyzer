import streamlit as st
import pandas as pd

from logic.analyzer import LabAnalyzer
from logic.interpretation import ClinicalInterpreter
from visuals.plots import abnormality_bar_chart, lab_vs_reference


# ------------------ App Config ------------------ #
st.set_page_config(
    page_title="Clinical Lab Results Analyzer",
    layout="wide"
)

st.title("🧪 Clinical Lab Results Analyzer")
st.caption("Educational clinical decision-support tool")

st.markdown(
    "**Disclaimer:** This tool is for educational and research purposes only and does not provide medical diagnoses."
)

# ------------------ Load Analyzer ------------------ #
analyzer = LabAnalyzer("reference_ranges.json")

# ------------------ Patient Info ------------------ #
st.subheader("Patient Information")

col1, col2 = st.columns(2)

with col1:
    sex = st.selectbox("Sex", ["male", "female"])

with col2:
    age = st.number_input("Age (years)", min_value=0, max_value=120, value=30)

# ------------------ Lab Input ------------------ #
st.subheader("Enter Lab Results")

cbc_tests = {
    "WBC": st.number_input("WBC (x10^9/L)", value=6.0),
    "RBC": st.number_input("RBC (x10^12/L)", value=4.8),
    "Hemoglobin": st.number_input("Hemoglobin (g/dL)", value=14.0),
    "Hematocrit": st.number_input("Hematocrit (%)", value=42.0),
    "Platelets": st.number_input("Platelets (x10^9/L)", value=250.0),
    "Neutrophils": st.number_input("Neutrophils (%)", value=55.0),
    "Lymphocytes": st.number_input("Lymphocytes (%)", value=30.0)
}

bmp_tests = {
    "Glucose": st.number_input("Glucose (mg/dL)", value=90.0),
    "Sodium": st.number_input("Sodium (mmol/L)", value=140.0),
    "Potassium": st.number_input("Potassium (mmol/L)", value=4.2),
    "Urea": st.number_input("Urea (mg/dL)", value=15.0),
    "Creatinine": st.number_input("Creatinine (mg/dL)", value=1.0)
}

# ------------------ Analyze Button ------------------ #
if st.button("Analyze Results"):

    analyzed_results = []

    for test, value in cbc_tests.items():
        analyzed_results.append(
            analyzer.analyze_test("CBC", test, value, sex)
        )

    for test, value in bmp_tests.items():
        analyzed_results.append(
            analyzer.analyze_test("BMP", test, value, sex)
        )

    # ------------------ Results Table ------------------ #
    st.subheader("Lab Results Summary")

    df = pd.DataFrame(analyzed_results)

    def highlight_status(row):
        if row["status"] == "High":
            return ["background-color: #f8d7da"] * len(row)
        elif row["status"] == "Low":
            return ["background-color: #fff3cd"] * len(row)
        else:
            return ["background-color: #d4edda"] * len(row)

    st.dataframe(
    df.style
        .apply(highlight_status, axis=1)
        .set_properties(**{
            "background-color": "#f5f7fa",   # soft grey background
            "color": "#1f2937",              # dark readable text
            "border-color": "#d1d5db"
        }),
    width="stretch"
)


    # ------------------ Visual Analysis ------------------ #
    st.subheader("Visual Analysis")

    fig1 = abnormality_bar_chart(df)
    st.plotly_chart(fig1, use_container_width=True)

    fig2 = lab_vs_reference(df)
    st.plotly_chart(fig2, use_container_width=True)

    # ------------------ Clinical Interpretation ------------------ #
    st.subheader("Clinical Interpretation")

    interpreter = ClinicalInterpreter(analyzed_results)
    insights = interpreter.interpret()

    for insight in insights:
        st.markdown(f"- {insight}")

    # ------------------ Clinical Summary Report ------------------ #
    st.subheader("Clinical Summary Report")

    abnormal_tests = df[df["status"] != "Normal"]

    if abnormal_tests.empty:
        st.success(
            "All analyzed laboratory parameters are within normal reference ranges."
        )
    else:
        st.markdown(
            f"""
            **Summary of Findings:**
            - {len(abnormal_tests)} abnormal laboratory parameter(s) detected.
            - Abnormal tests include: {", ".join(abnormal_tests['test'].tolist())}.
            """
        )

        st.markdown("**Interpretive Notes:**")
        for insight in insights:
            st.markdown(f"- {insight}")
