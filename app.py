# app.py
import streamlit as st
import pandas as pd
import os
from io import StringIO

st.set_page_config(page_title="Skillbot AI — Combined Tests", layout="wide")

# -----------------------
# Utility functions
# -----------------------
RIASEC_LOCAL_PATH = "/mnt/data/RIASEC test.csv"   # user's uploaded file path (if present)
TCI_LOCAL_PATH = "/mnt/data/TCT test.csv"         # user's uploaded file path (if present)

def try_read_csv(path):
    try:
        if os.path.exists(path):
            return pd.read_csv(path)
    except Exception:
        return None
    return None

def safe_read(uploaded_file):
    if uploaded_file is None:
        return None
    try:
        return pd.read_csv(uploaded_file)
    except Exception:
        # try read as text then parse
        text = StringIO(uploaded_file.getvalue().decode("utf-8"))
        return pd.read_csv(text)

# normalize TCI abbreviation mapping (if needed)
abbr_to_full = {
    "NS": "Novelty Seeking",
    "HA": "Harm Avoidance",
    "RD": "Reward Dependence",
    "P":  "Persistence",
    "SD": "Self-Directedness",
    "C":  "Cooperativeness",
    "ST": "Self-Transcendence"
}
full_to_abbr = {v: k for k, v in abbr_to_full.items()}

def normalize_riasec_df(df):
    # Accept dataframes that have either columns: Dimension, Score
    # or two columns with letters and scores. Return DataFrame with Dimension, Score
    if df is None:
        return None
    cols = [c.lower() for c in df.columns]
    # try common names
    if "dimension" in df.columns and "score" in df.columns:
        out = df[["Dimension","Score"]].copy()
    elif len(df.columns) >= 2:
        # pick first two columns
        out = df.iloc[:, :2].copy()
        out.columns = ["Dimension","Score"]
    else:
        return None
    # normalize Dimension values (strip)
    out["Dimension"] = out["Dimension"].astype(str).str.strip()
    out["Score"] = pd.to_numeric(out["Score"], errors="coerce").fillna(0).astype(int)
    return out

def normalize_tci_df(df):
    if df is None:
        return None
    if "Dimension" in df.columns and "Score" in df.columns:
        out = df[["Dimension","Score"]].copy()
    elif len(df.columns) >= 2:
        out = df.iloc[:, :2].copy()
        out.columns = ["Dimension","Score"]
    else:
        return None
    out["Dimension"] = out["Dimension"].astype(str).str.strip()
    out["Score"] = pd.to_numeric(out["Score"], errors="coerce").fillna(0).astype(int)
    # try to convert full names to abbreviations if needed
    out["Dimension_Abbr"] = out["Dimension"].apply(lambda v: full_to_abbr.get(v, v) if isinstance(v, str) else v)
    return out

# -----------------------
# Tabs (Option 2 style)
# -----------------------
tabs = st.tabs(["Home", "RIASEC Test", "TCI Test", "Dashboard", "Combined Report", "Uploads"])

# -----------------------
# Home
# -----------------------
with tabs[0]:
    st.title("Welcome to Skillbot AI — Combined RIASEC & TCI")
    st.write("""
    Use the tabs to take the **RIASEC** and **TCI** tests (one question at a time),
    view the **Dashboard**, and generate a **Combined Report**.
    """)
    st.markdown("**Quick tips:**")
    st.markdown("- If you already uploaded test *scores* as CSVs, go to **Uploads** and upload them or place them in the app's `/mnt/data/` folder.")
    st.markdown("- After completing tests, visit **Dashboard** and **Combined Report** to view and download results.")

# -----------------------
# RIASEC Test (Tab 2)
# -----------------------
with tabs[1]:
    st.header("RIASEC Test — One question at a time")
    st.write("If you have a question file `riasec_30_questions.csv` you can upload it here, otherwise the test UI will expect questions to be provided by a CSV.")

    qfile = st.file_uploader("Optional: Upload RIASEC questions CSV (columns: ID, Question, Dimension)", type=["csv"], key="riasec_questions_uploader")
    # try to load local question file if present
    riasec_questions = safe_read(qfile) if qfile else None
    # If no questions file, show message
    if riasec_questions is None:
        st.info("No RIASEC questions file uploaded. If you want to take the questionnaire here, upload a questions CSV with columns ID, Question, Dimension.")
        st.stop()

    # prepare questions
    riasec_questions.columns = riasec_questions.columns.str.strip()
    if "ID" not in riasec_questions.columns:
        riasec_questions.insert(0, "ID", range(1, len(riasec_questions)+1))
    # session state for riasec
    if "riasec_idx" not in st.session_state:
        st.session_state.riasec_idx = 0
    if "riasec_responses" not in st.session_state:
        st.session_state.riasec_responses = {}

    options = {
        1: "😐 Not at all",
        2: "🙂 Slightly",
        3: "😌 Moderately",
        4: "😄 Very Much",
        5: "🤩 Extremely"
    }

    def riasec_next():
        st.session_state.riasec_responses[st.session_state.riasec_idx] = st.session_state.get(f"riasec_q_{st.session_state.riasec_idx}", 3)
        st.session_state.riasec_idx += 1

    if st.session_state.riasec_idx < len(riasec_questions):
        idx = st.session_state.riasec_idx
        row = riasec_questions.iloc[idx]
        st.progress((idx+1)/len(riasec_questions))
        st.markdown(f"**Question {idx+1} of {len(riasec_questions)}**")
        st.markdown(f"### {row.get('Question')}")
        st.radio("How much would you enjoy this activity?", list(options.keys()), format_func=lambda x: options[x], key=f"riasec_q_{idx}")
        st.button("Next ➡️", on_click=riasec_next)
    else:
        # generate riasec results df
        qdf = riasec_questions.copy()
        qdf["Score"] = qdf["ID"].map(st.session_state.riasec_responses).fillna(3).astype(int)
        riasec_summary = qdf.groupby("Dimension")["Score"].sum().reset_index()
        st.success("RIASEC questionnaire completed!")
        st.subheader("RIASEC Scores")
        st.dataframe(riasec_summary)
        # store summary in session for other tabs
        st.session_state.riasec_summary = riasec_summary

# -----------------------
# TCI Test (Tab 3)
# -----------------------
with tabs[2]:
    st.header("TCI Test — One question at a time")
    st.write("Upload a TCI questions CSV (columns: ID, Question, Dimension) or use your own file.")

    tfile = st.file_uploader("Optional: Upload TCI questions CSV (25 items recommended)", type=["csv"], key="tci_questions_uploader")
    tci_questions = safe_read(tfile) if tfile else None
    if tci_questions is None:
        st.info("No TCI questions file uploaded. Upload a CSV to take the questionnaire here.")
        st.stop()

    tci_questions.columns = tci_questions.columns.str.strip()
    if "ID" not in tci_questions.columns:
        tci_questions.insert(0, "ID", range(1, len(tci_questions)+1))

    if "tci_idx" not in st.session_state:
        st.session_state.tci_idx = 0
    if "tci_responses" not in st.session_state:
        st.session_state.tci_responses = {}

    t_options = {
        1: "❌ Strongly Disagree",
        2: "😕 Disagree",
        3: "😐 Neutral",
        4: "🙂 Agree",
        5: "🔥 Strongly Agree"
    }

    def tci_next():
        st.session_state.tci_responses[st.session_state.tci_idx] = st.session_state.get(f"tci_q_{st.session_state.tci_idx}", 3)
        st.session_state.tci_idx += 1

    if st.session_state.tci_idx < len(tci_questions):
        idx = st.session_state.tci_idx
        row = tci_questions.iloc[idx]
        st.progress((idx+1)/len(tci_questions))
        st.markdown(f"**Question {idx+1} of {len(tci_questions)}**")
        st.markdown(f"### {row.get('Question')}")
        st.radio("Select your answer:", list(t_options.keys()), format_func=lambda x: t_options[x], key=f"tci_q_{idx}")
        st.button("Next ➡️", on_click=tci_next)
    else:
        tdf = tci_questions.copy()
        tdf["Score"] = tdf["ID"].map(st.session_state.tci_responses).fillna(3).astype(int)
        # map dimension names -> abbreviations if needed
        # assume tci_questions has full names like "Novelty Seeking" or already abbreviation
        def to_abbr(x):
            x = str(x).strip()
            return full_to_abbr.get(x, x)
        tdf["Dim_Abbr"] = tdf["Dimension"].apply(to_abbr)
        tci_summary = tdf.groupby("Dim_Abbr")["Score"].sum().reset_index().rename(columns={"Dim_Abbr":"Dimension"})
        st.success("TCI questionnaire completed!")
        st.subheader("TCI Scores")
        st.dataframe(tci_summary)
        st.session_state.tci_summary = tci_summary

# -----------------------
# Dashboard (Tab 4)
# -----------------------
with tabs[3]:
    st.header("Combined Dashboard")
    st.write("This dashboard shows RIASEC & TCI scores from either (a) completed tests in this session, (b) uploaded score CSVs, or (c) files in `/mnt/data/`.")

    # Try session data first
    riasec_df_session = st.session_state.get("riasec_summary", None)
    tci_df_session = st.session_state.get("tci_summary", None)

    # Try local paths if present
    riasec_local = try_read_csv(RIASEC_LOCAL_PATH)
    tci_local = try_read_csv(TCI_LOCAL_PATH)

    # Also allow user to upload score CSVs
    riasec_scores_upload = st.file_uploader("Upload RIASEC scores CSV (Dimension,Score) — optional", type=["csv"], key="riasec_scores_up")
    tci_scores_upload = st.file_uploader("Upload TCI scores CSV (Dimension,Score) — optional", type=["csv"], key="tci_scores_up")

    riasec_df = None
    tci_df = None

    # precedence: session -> uploaded -> local
    if riasec_df_session is not None:
        riasec_df = riasec_df_session.copy()
    elif riasec_scores_upload:
        riasec_df = safe_read(riasec_scores_upload)
        riasec_df = normalize_riasec_df(riasec_df)
    elif riasec_local is not None:
        riasec_df = normalize_riasec_df(riasec_local)

    if tci_df_session is not None:
        tci_df = tci_df_session.copy()
    elif tci_scores_upload:
        tci_df = safe_read(tci_scores_upload)
        tci_df = normalize_tci_df(tci_df)
        # make column name consistent
        if "Dimension_Abbr" in tci_df.columns:
            tci_df = tci_df.rename(columns={"Dimension_Abbr": "Dimension"})
    elif tci_local is not None:
        tci_df = normalize_tci_df(tci_local)
        if "Dimension_Abbr" in tci_df.columns:
            tci_df = tci_df.rename(columns={"Dimension_Abbr": "Dimension"})

    if riasec_df is None and tci_df is None:
        st.info("No score data available yet. Complete tests or upload score CSVs (or place files in /mnt/data/).")
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("RIASEC Scores")
            if riasec_df is not None:
                # ensure index and types
                riasec_df = riasec_df.copy()
                riasec_df["Score"] = pd.to_numeric(riasec_df["Score"], errors="coerce").fillna(0)
                st.dataframe(riasec_df)
                st.bar_chart(riasec_df.set_index("Dimension")["Score"])
            else:
                st.info("No RIASEC data available.")

        with col2:
            st.subheader("TCI Scores")
            if tci_df is not None:
                tci_df = tci_df.copy()
                tci_df["Score"] = pd.to_numeric(tci_df["Score"], errors="coerce").fillna(0)
                st.dataframe(tci_df)
                st.bar_chart(tci_df.set_index("Dimension")["Score"])
            else:
                st.info("No TCI data available.")

        st.markdown("---")
        st.subheader("Combined Insights")
        if riasec_df is not None:
            top_r = riasec_df.sort_values("Score", ascending=False).iloc[0]["Dimension"]
            st.markdown(f"**Top RIASEC:** {top_r}")
        if tci_df is not None:
            top_t = tci_df.sort_values("Score", ascending=False).iloc[0]["Dimension"]
            st.markdown(f"**Top TCI:** {top_t}")

# -----------------------
# Combined Report (Tab 5)
# -----------------------
with tabs[4]:
    st.header("Combined Report")
    st.write("Generate a combined text summary and download scores as CSV.")

    # try to prepare combined df as in Dashboard
    riasec_df = st.session_state.get("riasec_summary") or try_read_csv(RIASEC_LOCAL_PATH)
    tci_df_raw = st.session_state.get("tci_summary") or try_read_csv(TCI_LOCAL_PATH)

    # normalize if raw
    if isinstance(riasec_df, pd.DataFrame) and "Dimension" in riasec_df.columns and "Score" in riasec_df.columns:
        riasec_df = normalize_riasec_df(riasec_df)
    if isinstance(tci_df_raw, pd.DataFrame):
        tci_df = normalize_tci_df(tci_df_raw)
        if "Dimension_Abbr" in tci_df.columns:
            tci_df = tci_df.rename(columns={"Dimension_Abbr":"Dimension"})
    else:
        tci_df = None

    if riasec_df is None and tci_df is None:
        st.info("No data available to build the report. Complete tests or upload score CSVs.")
    else:
        # Build textual summary
        summary_lines = []
        if riasec_df is not None:
            r_top = riasec_df.sort_values("Score", ascending=False).iloc[0]
            summary_lines.append(f"Top RIASEC dimension: {r_top['Dimension']} (Score: {r_top['Score']})")
            summary_lines.append("RIASEC breakdown:")
            for _, r in riasec_df.sort_values("Score", ascending=False).iterrows():
                summary_lines.append(f" - {r['Dimension']}: {r['Score']}")

        if tci_df is not None:
            t_top = tci_df.sort_values("Score", ascending=False).iloc[0]
            summary_lines.append(f"Top TCI trait: {t_top['Dimension']} (Score: {t_top['Score']})")
            summary_lines.append("TCI breakdown:")
            for _, t in tci_df.sort_values("Score", ascending=False).iterrows():
                summary_lines.append(f" - {t['Dimension']}: {t['Score']}")

        # combined suggestions (simple rule-based)
        suggestions = []
        if riasec_df is not None and tci_df is not None:
            # example rule: if R high and SD high -> engineering careers suggested
            r_top_dim = riasec_df.sort_values("Score", ascending=False).iloc[0]["Dimension"]
            t_top_dim = tci_df.sort_values("Score", ascending=False).iloc[0]["Dimension"]
            suggestions.append(f"Considering your top interest {r_top_dim} and temperament {t_top_dim}, consider exploring related fields and programs.")
        else:
            suggestions.append("Complete both tests for combined recommendations.")

        report_text = "\n".join(summary_lines + ["", "Recommendations:"] + suggestions)
        st.markdown("### Combined Summary")
        st.text(report_text)

        # prepare combined CSV for download
        parts = []
        if riasec_df is not None:
            rcopy = riasec_df.copy()
            rcopy["Source"] = "RIASEC"
            parts.append(rcopy.rename(columns={"Dimension":"Dimension","Score":"Score"}))
        if tci_df is not None:
            tcopy = tci_df.copy()
            tcopy["Source"] = "TCI"
            parts.append(tcopy.rename(columns={"Dimension":"Dimension","Score":"Score"}))
        combined_csv_df = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()
        csv_bytes = combined_csv_df.to_csv(index=False).encode("utf-8")
        st.download_button("Download combined scores CSV", data=csv_bytes, file_name="combined_scores.csv", mime="text/csv")

# -----------------------
# Uploads (Tab 6)
# -----------------------
with tabs[5]:
    st.header("Uploads & Local files")
    st.write("You can upload score CSVs or questions CSVs here. The app will also try to read files placed at:")
    st.code(RIASEC_LOCAL_PATH)
    st.code(TCI_LOCAL_PATH)

    st.markdown("### Upload or overwrite local score files")
    up_r = st.file_uploader("Upload RIASEC scores CSV (Dimension,Score) — will not overwrite local file automatically", accept_multiple_files=False, key="upload_scores_r")
    up_t = st.file_uploader("Upload TCI scores CSV (Dimension,Score) — will not overwrite local file automatically", accept_multiple_files=False, key="upload_scores_t")

    if up_r:
        st.success("RIASEC scores file uploaded for session.")
        df_r = safe_read(up_r)
        st.dataframe(df_r)
        st.session_state["riasec_summary"] = normalize_riasec_df(df_r)

    if up_t:
        st.success("TCI scores file uploaded for session.")
        df_t = safe_read(up_t)
        df_tn = normalize_tci_df(df_t)
        if "Dimension_Abbr" in df_tn.columns:
            df_tn = df_tn.rename(columns={"Dimension_Abbr":"Dimension"})
        st.dataframe(df_tn)
        st.session_state["tci_summary"] = df_tn

    st.markdown("---")
    st.info("If you want these files permanently available in the app without uploading each time, place them in the app's /mnt/data/ folder named exactly:\n- RIASEC test.csv\n- TCT test.csv\n(Your environment or deployment method determines whether you can write to /mnt/data/.)")
