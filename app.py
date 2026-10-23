
import sqlite3
from pathlib import Path
from datetime import date

import pandas as pd
import streamlit as st


# =====================================
# 1. APP CONFIGURATION
# =====================================

st.set_page_config(
    page_title="India Cancer Patient Registry",
    page_icon="🩺",
    layout="wide"
)

DB_PATH = Path(__file__).resolve().parent / "cancer_registry.db"


# =====================================
# 2. DATABASE
# =====================================

def initialize_database():
    conn = sqlite3.connect(DB_PATH)

    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_code TEXT UNIQUE NOT NULL,
                age INTEGER NOT NULL,
                sex TEXT NOT NULL,
                state TEXT NOT NULL,
                district TEXT,
                hospital_code TEXT NOT NULL,
                cancer_type TEXT NOT NULL,
                diagnosis_date TEXT,
                cancer_stage TEXT NOT NULL,
                treatment_status TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    finally:
        conn.close()


def get_patients():
    conn = sqlite3.connect(DB_PATH)

    try:
        return pd.read_sql_query("""
            SELECT patient_code, age, sex, state, district,
                   hospital_code, cancer_type, diagnosis_date,
                   cancer_stage, treatment_status, created_at
            FROM patients
            ORDER BY id DESC
        """, conn)
    finally:
        conn.close()


initialize_database()


# =====================================
# 3. OPTIONS FOR THE FORMS
# =====================================

STATES = [
    "Andhra Pradesh",
    "Assam",
    "Bihar",
    "Chhattisgarh",
    "Delhi",
    "Goa",
    "Gujarat",
    "Haryana",
    "Himachal Pradesh",
    "Jharkhand",
    "Karnataka",
    "Kerala",
    "Madhya Pradesh",
    "Maharashtra",
    "Manipur",
    "Meghalaya",
    "Mizoram",
    "Nagaland",
    "Odisha",
    "Punjab",
    "Rajasthan",
    "Sikkim",
    "Tamil Nadu",
    "Telangana",
    "Tripura",
    "Uttar Pradesh",
    "Uttarakhand",
    "West Bengal",
    "Other / Unknown"
]

CANCER_TYPES = [
    "Breast",
    "Oral cavity",
    "Lung",
    "Cervix",
    "Colorectal",
    "Prostate",
    "Stomach",
    "Blood / Leukaemia",
    "Ovary",
    "Liver",
    "Other",
    "Unknown"
]

STAGES = [
    "Unknown",
    "Stage 0",
    "Stage I",
    "Stage II",
    "Stage III",
    "Stage IV"
]

TREATMENTS = [
    "Not started",
    "Surgery",
    "Chemotherapy",
    "Radiotherapy",
    "Immunotherapy / targeted therapy",
    "Palliative / supportive care",
    "Completed",
    "Unknown"
]

SEX_OPTIONS = [
    "Female",
    "Male",
    "Intersex",
    "Prefer not to say",
    "Unknown"
]


# =====================================
# 4. SIDEBAR MENU
# =====================================

st.sidebar.title("🩺 Cancer Registry")

page = st.sidebar.radio(
    "Choose a page",
    [
        "Dashboard",
        "Register Patient",
        "View Records"
    ]
)

st.sidebar.divider()
st.sidebar.caption("India Cancer Patient Registry - Prototype")


# =====================================
# 5. DASHBOARD
# =====================================

if page == "Dashboard":

    st.title("India Cancer Patient Registry")

    st.write(
        "A prototype for collecting and analysing "
        "coded cancer patient records."
    )

    df = get_patients()

    col1, col2, col3 = st.columns(3)

    col1.metric("Total patient records", len(df))

    col2.metric(
        "States / UTs",
        df["state"].nunique() if not df.empty else 0
    )

    col3.metric(
        "Hospitals",
        df["hospital_code"].nunique() if not df.empty else 0
    )

    st.divider()

    if df.empty:

        st.info(
            "No records available. Select Register Patient "
            "from the sidebar to add a test record."
        )

    else:

        left, right = st.columns(2)

        with left:
            st.subheader("Cancer types")
            st.bar_chart(df["cancer_type"].value_counts())

        with right:
            st.subheader("Records by state")
            st.bar_chart(df["state"].value_counts())

        st.subheader("Cancer stages")
        st.bar_chart(df["cancer_stage"].value_counts())

    st.caption(
        "These figures represent records entered in this app, "
        "not cancer incidence estimates for India."
    )


# =====================================
# 6. REGISTER A PATIENT
# =====================================

elif page == "Register Patient":

    st.title("Register a Cancer Patient")

    st.warning(
        "Use fictional data while testing. Do not enter names, "
        "Aadhaar numbers, phone numbers, or other direct identifiers."
    )

    with st.form("patient_form"):

        col1, col2 = st.columns(2)

        with col1:

            age = st.number_input(
                "Age at diagnosis",
                min_value=0,
                max_value=120,
                value=50,
                step=1
            )

            sex = st.selectbox(
                "Sex",
                SEX_OPTIONS
            )

            state = st.selectbox(
                "State / Union Territory",
                STATES
            )

            district = st.text_input(
                "District (optional)"
            )

            hospital_code = st.text_input(
                "Hospital code",
                placeholder="HOSP-001"
            )

        with col2:

            cancer_type = st.selectbox(
                "Cancer type",
                CANCER_TYPES
            )

            diagnosis_date_text = st.text_input(
                "Diagnosis date (optional)",
                placeholder="YYYY-MM-DD"
            )

            cancer_stage = st.selectbox(
                "Cancer stage",
                STAGES
            )

            treatment_status = st.selectbox(
                "Treatment status",
                TREATMENTS
            )

        submitted = st.form_submit_button(
            "Save Patient Record",
            type="primary"
        )

    if submitted:

        # Validate diagnosis date if supplied
        parsed_date = None
        date_error = False

        if diagnosis_date_text.strip():

            try:
                parsed_date = date.fromisoformat(
                    diagnosis_date_text.strip()
                )

                if parsed_date > date.today():
                    st.error("Diagnosis date cannot be in the future.")
                    date_error = True

            except ValueError:
                st.error(
                    "Enter the date in YYYY-MM-DD format, "
                    "for example 2026-04-10."
                )
                date_error = True

        if date_error:
            pass

        elif not hospital_code.strip():

            st.error("Please enter the hospital code.")

        else:

            conn = sqlite3.connect(DB_PATH)

            try:

                next_id = conn.execute(
                    "SELECT COALESCE(MAX(id), 0) + 1 FROM patients"
                ).fetchone()[0]

                patient_code = f"IND-{next_id:06d}"

                conn.execute("""
                    INSERT INTO patients (
                        patient_code,
                        age,
                        sex,
                        state,
                        district,
                        hospital_code,
                        cancer_type,
                        diagnosis_date,
                        cancer_stage,
                        treatment_status
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    patient_code,
                    int(age),
                    sex,
                    state,
                    district.strip() or None,
                    hospital_code.strip(),
                    cancer_type,
                    parsed_date.isoformat() if parsed_date else None,
                    cancer_stage,
                    treatment_status
                ))

                conn.commit()

                st.success("Patient record saved successfully!")

                st.info(
                    f"Generated Patient Code: {patient_code}"
                )

            except sqlite3.Error:
                st.error(
                    "Database error. The record could not be saved."
                )

            finally:
                conn.close()


# =====================================
# 7. VIEW AND SEARCH PATIENT RECORDS
# =====================================

elif page == "View Records":

    st.title("Patient Records")

    df = get_patients()

    if df.empty:

        st.info("No records found. Register a test patient first.")

    else:

        search_code = st.text_input(
            "Search by patient code",
            placeholder="IND-000001"
        )

        filtered_df = df.copy()

        if search_code.strip():

            filtered_df = filtered_df[
                filtered_df["patient_code"].str.contains(
                    search_code.strip(),
                    case=False,
                    na=False
                )
            ]

        st.write(f"Records found: {len(filtered_df)}")

        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True
        )

        csv_data = filtered_df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            label="Download records as CSV",
            data=csv_data,
            file_name="cancer_patient_records.csv",
            mime="text/csv"
        )
