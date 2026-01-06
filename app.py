# ----------------- Imports -----------------
import streamlit as st
import pandas as pd

# ----------------- Internal Modules -----------------
from logic.analyzer import LabAnalyzer
from logic.interpretation import ClinicalInterpreter
from visuals.plots import abnormality_bar_chart, lab_vs_reference


# ------------------ App Config ------------------ #
st.set_page_config(
    page_title="Clinical Lab Results Analyzer",
    layout="wide"
)

# ------------------ App Header ------------------ #
st.title("🧪 Clinical Lab Results Analyzer")
st.caption("Educational clinical decision-support tool")

st.markdown(
    "**Disclaimer:** This tool is for educational and research purposes only."
)

# ----------------- Analysis Mode ----------------- #
st.subheader("Analysis Mode")

mode = st.radio(
    "Select how you want to analyze data:",
    ("Manual Entry", "Upload CSV/Excel File")
)

# ------------------ Load Analyzer ------------------ #
analyzer = LabAnalyzer("reference_ranges.json")

# ==================================================
# =============== MANUAL ENTRY MODE ================
# ==================================================
if mode == "Manual Entry":
    st.subheader("Patient Information")

    col1, col2 = st.columns(2)

    with col1:
        sex = st.selectbox("Sex", ["male", "female"])

    with col2:
        age = st.number_input("Age (years)", min_value=0, max_value=120, value=30)

    st.subheader("Enter Lab Results")

    cbc_tests = {
        "WBC": st.number_input("WBC (x10^9/L)", value=6.0),
        "RBC": st.number_input("RBC (x10^12/L)", value=4.8),
        "Hemoglobin": st.number_input("Hemoglobin (g/dL)", value=14.0),
        "Hematocrit": st.number_input("Hematocrit (%)", value=42.0),
        "Platelets": st.number_input("Platelets (x10^9/L)", value=250.0),
        "Neutrophils": st.number_input("Neutrophils (%)", value=55.0),
        "Lymphocytes": st.number_input("Lymphocytes (%)", value=30.0),
    }

    bmp_tests = {
        "Glucose": st.number_input("Glucose (mg/dL)", value=90.0),
        "Sodium": st.number_input("Sodium (mmol/L)", value=140.0),
        "Potassium": st.number_input("Potassium (mmol/L)", value=4.2),
        "Urea": st.number_input("Urea (mg/dL)", value=15.0),
        "Creatinine": st.number_input("Creatinine (mg/dL)", value=1.0),
    }

# ==================================================
# =============== FILE UPLOAD MODE =================
# ==================================================
else:
    st.subheader("Upload Lab Results File")

    uploaded_file = st.file_uploader(
        "Upload a CSV or Excel file",
        type=["csv", "xlsx"]
    )

    st.markdown(
        """
        **Required Columns:**
        - test  
        - value  
        - sex  
        """
    )

# ==================================================
# ================= ANALYSIS =======================
# ==================================================
if st.button("Analyze Results"):

    # -------- Manual Entry Analysis -------- #
    if mode == "Manual Entry":
        analyzed_results = []

        for test, value in cbc_tests.items():
            analyzed_results.append(
                analyzer.analyze_test("CBC", test, value, sex)
            )

        for test, value in bmp_tests.items():
            analyzed_results.append(
                analyzer.analyze_test("BMP", test, value, sex)
            )

        df_results = pd.DataFrame(analyzed_results)

    # -------- File Upload Analysis -------- #
    else:
        if uploaded_file is None:
            st.error("Please upload a file before analysis.")
            st.stop()

        if uploaded_file.name.endswith(".csv"):
            df_input = pd.read_csv(uploaded_file)
        else:
            df_input = pd.read_excel(uploaded_file)

        df_results = analyzer.analyze_dataframe(df_input)

    # ==================================================
    # ================= RESULTS ========================
    # ==================================================
    st.subheader("Lab Results Summary")

    def highlight_status(row):
        if row["status"] == "High":
            return ["background-color: #f8d7da"] * len(row)
        elif row["status"] == "Low":
            return ["background-color: #fff3cd"] * len(row)
        else:
            return ["background-color: #d4edda"] * len(row)

    st.dataframe(
        df_results.style.apply(highlight_status, axis=1),
        use_container_width=True
    )

    # ------------------ Visual Analysis ------------------ #
    st.subheader("Visual Analysis")

    st.plotly_chart(
        abnormality_bar_chart(df_results),
        use_container_width=True
    )

    st.plotly_chart(
        lab_vs_reference(df_results),
        use_container_width=True
    )

    # ------------------ Clinical Interpretation ------------------ #
    st.subheader("Clinical Interpretation")

    interpreter = ClinicalInterpreter(df_results)
    insights = interpreter.interpret()

    for insight in insights:
        st.markdown(f"- {insight}")

    # ------------------ Summary Report ------------------ #
    st.subheader("Clinical Summary Report")

    abnormal_tests = df_results[df_results["status"] != "Normal"]

    if abnormal_tests.empty:
        st.success("All laboratory values are within normal ranges.")
    else:
        st.markdown(
            f"""
            **Summary of Findings**
            - {len(abnormal_tests)} abnormal parameter(s)
            - Affected tests: {", ".join(abnormal_tests['test'].tolist())}
            """
        )
