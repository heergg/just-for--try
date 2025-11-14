import streamlit as st
import pandas as pd

# Load CSVs
df = pd.read_csv("riasec_30_questions.csv")
meanings_df = pd.read_csv("riasec_meanings.csv")  # RIASEC meanings CSV

st.title("RIASEC Interest Test 🎯")
st.write("Rate each activity based on **how much you would enjoy doing it**.")

# Emoji Options
options = {
    1: "😐 Not at all",
    2: "🙂 Slightly",
    3: "😌 Moderately",
    4: "😄 Very Much",
    5: "🤩 Extremely"
}

# Initialize session state
if "index" not in st.session_state:
    st.session_state.index = 0
if "responses" not in st.session_state:
    st.session_state.responses = {}

def next_question():
    st.session_state.responses[st.session_state.index] = st.session_state[f"q_{st.session_state.index}"]
    st.session_state.index += 1

# If all questions done
if st.session_state.index >= len(df):
    # Assign scores
    df["Score"] = df["ID"].map(st.session_state.responses)
    scores = df.groupby("Dimension")["Score"].sum().to_dict()

    st.success("🎉 You have completed the RIASEC Test!")
    st.subheader("📌 Your RIASEC Interest Scores")
    st.write(scores)

    # Generate profile with meanings
    def generate_profile_with_meanings(scores, meanings_df):
        sorted_dim = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top3 = [d for d, _ in sorted_dim[:3]]

        profile_text = "### 🎨 Your RIASEC Interest Profile\n\n**Top 3 Interests:**\n"
        for dim in top3:
            meaning = meanings_df.loc[meanings_df["Dimension"] == dim, "Meaning"].values[0]
            profile_text += f"- **{dim}** → {meaning}\n"

        profile_text += "\n**Detailed Scores:**\n"
        for dim, score in scores.items():
            profile_text += f"- {dim}: {score}\n"

        return profile_text

    st.markdown(generate_profile_with_meanings(scores, meanings_df))

else:
    # Display current question
    idx = st.session_state.index
    row = df.iloc[idx]

    st.markdown(f"## Question {row['ID']}")
    st.markdown(f"### {row['Question']}")

    st.radio(
        "How much would you enjoy this activity?",
        list(options.keys()),
        format_func=lambda x: options[x],
        key=f"q_{idx}"
    )

    st.button("Next ➡️", on_click=next_question)

