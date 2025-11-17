import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Combined RIASEC + TCI Dashboard", layout="wide")

st.title("🧠 Combined RIASEC + TCI Personality Dashboard")

# -----------------------------
# File Upload Section
# -----------------------------
st.sidebar.header("📂 Upload Your Test Files")

riasec_file = st.sidebar.file_uploader("Upload RIASEC CSV", type=["csv"])
tci_file = st.sidebar.file_uploader("Upload TCI CSV", type=["csv"])


# -----------------------------
# When both files are uploaded
# -----------------------------
if riasec_file and tci_file:

    # Read files
    riasec_df = pd.read_csv(riasec_file)
    tci_df = pd.read_csv(tci_file)

    st.success("Files uploaded successfully!")

    # -----------------------------
    # RIASEC Section
    # -----------------------------
    st.header("🎯 RIASEC Interest Profile")
    st.dataframe(riasec_df)

    # Bar Chart – RIASEC
    st.subheader("📊 RIASEC Score Chart")

    fig1, ax1 = plt.subplots()
    ax1.bar(riasec_df["Dimension"], riasec_df["Score"])
    plt.xlabel("RIASEC Dimensions")
    plt.ylabel("Scores")
    plt.title("RIASEC Personality Scores")
    st.pyplot(fig1)

    # -----------------------------
    # TCI Section
    # -----------------------------
    st.header("🧬 TCI Temperament & Character Profile")
    st.dataframe(tci_df)

    # Bar Chart – TCI
    st.subheader("📈 TCI Score Chart")

    fig2, ax2 = plt.subplots()
    ax2.bar(tci_df["Dimension"], tci_df["Score"])
    plt.xlabel("TCI Dimensions")
    plt.ylabel("Scores")
    plt.title("TCI Temperament & Character Scores")
    st.pyplot(fig2)

    # -----------------------------
    # Combined Interpretation
    # -----------------------------
    st.header("🔍 Combined Personality Interpretation")

    def interpret_riasec(riasec_df):
        highest = riasec_df.sort_values("Score", ascending=False).iloc[0]
        dim = highest["Dimension"]
        meanings = {
            "R": "Realistic – Practical, Hands-on",
            "I": "Investigative – Analytical, Curious",
            "A": "Artistic – Creative, Imaginative",
            "S": "Social – Helping, Cooperative",
            "E": "Enterprising – Leadership, Influencing",
            "C": "Conventional – Organized, Detail-oriented"
        }
        return f"**Top RIASEC Type: {dim} → {meanings.get(dim, 'Unknown')}**"

    def interpret_tci(tci_df):
        highest = tci_df.sort_values("Score", ascending=False).iloc[0]
        dim = highest["Dimension"]
        return f"**Dominant TCI Trait: {dim}**"

    st.markdown(interpret_riasec(riasec_df))
    st.markdown(interpret_tci(tci_df))

    # -----------------------------
    # Combined Summary
    # -----------------------------
    st.header("🧩 Combined Personality Summary")

    combined_summary = f"""
### ⭐ Final Combined Personality Summary

**RIASEC insights:**  
Your career interests are primarily guided by **{riasec_df.sort_values("Score", ascending=False).iloc[0]["Dimension"]}**,  
showing the type of work you naturally enjoy.

**TCI insights:**  
Your temperament is shaped strongly by **{tci_df.sort_values("Score", ascending=False).iloc[0]["Dimension"]}**,  
which reflects emotional and decision-making tendencies.

Together, these tests show how your **career interests (RIASEC)**  
and **temperament/character (TCI)** combine to create your unique personality profile.
"""

    st.markdown(combined_summary)

else:
    st.info("Please upload both CSV files to generate your dashboard.")
