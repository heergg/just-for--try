import streamlit as st
import pandas as pd

# Load CSV
df = pd.read_csv("riasec_30_questions.csv")

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

    # Generate profile
    def generate_profile(scores):
        sorted_dim = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top3 = [d for d, _ in sorted_dim[:3]]
        return f"""
### 🎨 Your RIASEC Interest Profile

**Top 3 Interests:**
1️⃣ **{top3[0]}**  
2️⃣ **{top3[1]}**  
3️⃣ **{top3[2]}**

**Detailed Scores:**
- Realistic (R): {scores['R']}
- Investigative (I): {scores['I']}
- Artistic (A): {scores['A']}
- Social (S): {scores['S']}
- Enterprising (E): {scores['E']}
- Conventional (C): {scores['C']}
"""
    st.markdown(generate_profile(scores))

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
