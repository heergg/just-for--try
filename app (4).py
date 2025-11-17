import streamlit as st
import pandas as pd

# Load TCI CSV
df = pd.read_csv("tci_25_questions (1).csv")

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

# Session State
if "index_tci" not in st.session_state:
    st.session_state.index_tci = 0

if "tci_responses" not in st.session_state:
    st.session_state.tci_responses = {}

# Function — Next Question
def next_tci_question():
    st.session_state.tci_responses[st.session_state.index_tci] = \
        st.session_state[f"tci_q_{st.session_state.index_tci}"]
    st.session_state.index_tci += 1

# After last question
if st.session_state.index_tci >= len(df):

    # Assign scores into dataframe
    df["Score"] = df["ID"].map(st.session_state.tci_responses)
    
    # Calculate dimension-wise scores
    scores = df.groupby("Dimension")["Score"].sum().to_dict()

    st.success("🎉 You have completed the TCI Test!")
    st.subheader("📌 Your TCI Personality Scores")
    st.write(scores)

    # Profile Generator
    def generate_tci_profile(scores):
        descriptions = {
            "NS": "High novelty seekers are curious, impulsive, and always ready for new adventures.",
            "HA": "High harm avoidance individuals are cautious, careful, and easily stressed.",
            "RD": "Reward dependent people are warm, loving, and sensitive to social approval.",
            "P": "Persistent individuals are determined, hard-working, and goal-oriented.",
            "SD": "Self-directed individuals are responsible, purposeful, and motivated.",
            "C": "Cooperative individuals are empathetic, kind, and supportive.",
            "ST": "Self-transcendent people are spiritual, imaginative, and intuitive."
        }

        profile = "## 🧬 Your TCI Personality Profile\n\n"

        for dim, score in scores.items():
            full_name = df.loc[df.Dimension == dim, "Dimension_FullName"].iloc[0]
            meaning = descriptions[dim]

            profile += f"""
### **{full_name} ({dim})**
- **Score:** {score}
- **About You:** {meaning}

"""

        return profile

    st.markdown(generate_tci_profile(scores))

else:
    # Ask current question
    idx = st.session_state.index_tci
    row = df.iloc[idx]

    st.markdown(f"## Question {row['ID']}")
    st.write(row["Question"])

    st.radio(
        "Select your answer:",
        list(options.keys()),
        format_func=lambda x: options[x],
        key=f"tci_q_{idx}"
    )

    st.button("Next ➡️", on_click=next_tci_question)
