import streamlit as st
import pandas as pd

# Load TCI CSV
try:
    df = pd.read_csv("tci_25_questions.csv")
except FileNotFoundError:
    st.error("tci_25_questions.csv not found in app folder.")
    st.stop()

st.title("TCI Personality Test 🧠")
st.write("Rate each statement based on **how well it describes you**.")

# Likert Options
options = {
    1: "❌ Strongly Disagree",
    2: "😕 Disagree",
    3: "😐 Neutral",
    4: "🙂 Agree",
    5: "🔥 Strongly Agree"
}

# Canonical mappings
abbr_to_full = {
    "NS": "Novelty Seeking",
    "HA": "Harm Avoidance",
    "RD": "Reward Dependence",
    "P":  "Persistence",
    "SD": "Self-Directedness",
    "C":  "Cooperativeness",
    "ST": "Self-Transcendence"
}
# Inverse map
full_to_abbr = {v: k for k, v in abbr_to_full.items()}

# Normalize the Dimension column in dataframe to abbreviations
def normalize_dimension(value):
    if pd.isna(value):
        return value
    value = str(value).strip()
    if value in abbr_to_full:
        return value  # already abbreviation
    if value in full_to_abbr:
        return full_to_abbr[value]  # full name -> abbr
    # try case-insensitive match
    for full, abbr in full_to_abbr.items():
        if value.lower() == full.lower():
            return abbr
    # fallback: return original truncated uppercase (best-effort)
    return value[:2].upper()

df["Dimension_Abbr"] = df["Dimension"].apply(normalize_dimension)

# Session state for one-by-one questions
if "index_tci" not in st.session_state:
    st.session_state.index_tci = 0
if "tci_responses" not in st.session_state:
    st.session_state.tci_responses = {}

def next_tci_question():
    st.session_state.tci_responses[st.session_state.index_tci] = \
        st.session_state.get(f"tci_q_{st.session_state.index_tci}", 3)
    st.session_state.index_tci += 1

# Ask questions one-by-one
if st.session_state.index_tci < len(df):
    idx = st.session_state.index_tci
    row = df.iloc[idx]

    st.progress((idx+1)/len(df))
    st.markdown(f"**Question {idx+1} of {len(df)}**")
    st.markdown(f"### {row['Question']}")
    st.radio(
        "Select your answer:",
        list(options.keys()),
        format_func=lambda x: options[x],
        key=f"tci_q_{idx}"
    )
    st.button("Next ➡️", on_click=next_tci_question)

else:
    # Build scores grouped by canonical abbreviation
    # Map responses by question ID => score, then attach to df
    # Note: ensure IDs in CSV are numeric and match response keys
    resp_map = {int(k)+1: v for k, v in st.session_state.tci_responses.items()}  
    # If your ID index starts at 1 use that; above converts 0-based session index -> 1-based ID
    # If your IDs already match the session_state keys remove the +1 logic

    # Try to map by df index first; fallback to 'ID' column
    if "ID" in df.columns:
        df["Score"] = df["ID"].map(resp_map).fillna(3).astype(int)
    else:
        df["Score"] = df.index.map(lambda i: st.session_state.tci_responses.get(i, 3))

    # Group by abbreviation
    scores_series = df.groupby("Dimension_Abbr")["Score"].sum()
    scores = scores_series.to_dict()  # e.g., {'NS': 42, 'HA': 37, ...}

    # Ensure all canonical dims are present (fill zeros for missing)
    for abbr in abbr_to_full:
        scores.setdefault(abbr, 0)

    st.success("🎉 You have completed the TCI Test!")
    st.subheader("📌 Your TCI Personality Scores (by dimension)")

    # Show scores with full names
    display_df = pd.DataFrame([
        {"Dimension_Abbr": abbr, "Dimension_Full": abbr_to_full.get(abbr, abbr), "Score": scores[abbr]}
        for abbr in abbr_to_full
    ])
    st.dataframe(display_df.set_index("Dimension_Abbr"))

    # Profile generator (robust)
    def generate_tci_profile(scores_dict):
        descriptions = {
            "NS": "High novelty seekers are curious, impulsive, and always ready for new adventures.",
            "HA": "High harm avoidance individuals are cautious, careful, and easily stressed.",
            "RD": "Reward dependent people are warm, loving, and sensitive to social approval.",
            "P":  "Persistent individuals are determined, hard-working, and goal-oriented.",
            "SD": "Self-directed individuals are responsible, purposeful, and motivated.",
            "C":  "Cooperative individuals are empathetic, kind, and supportive.",
            "ST": "Self-transcendent people are spiritual, imaginative, and intuitive."
        }

        # sort by score descending
        sorted_items = sorted(scores_dict.items(), key=lambda x: x[1], reverse=True)
        profile_md = "## 🧬 Your TCI Personality Profile\n\n"
        profile_md += "### Top Dimensions (by score)\n"
        for abbr, sc in sorted_items[:3]:
            profile_md += f"- **{abbr} — {abbr_to_full.get(abbr, abbr)}** (Score: {sc})\n"
        profile_md += "\n---\n"

        for abbr, sc in sorted_items:
            full = abbr_to_full.get(abbr, abbr)
            desc = descriptions.get(abbr, "No description available.")
            profile_md += f"### **{full} ({abbr})**\n- **Score:** {sc}\n- **About You:** {desc}\n\n"

        return profile_md

    st.markdown(generate_tci_profile(scores))

    # Optional: simple bar chart without external libs
    st.subheader("📈 Visual Overview")
    st.bar_chart(pd.Series({abbr_to_full[k]: v for k, v in scores.items()}))
