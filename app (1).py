import streamlit as st
import pandas as pd

# Load your CSV
df = pd.read_csv("/content/riasec_30_questions.csv")

st.title("RIASEC Interest Test 🎯")

st.write("Please rate each activity based on **how much you would enjoy doing it**.")

# Step-1 Options with Emojis
options = {
    1: "😐 Not at all",
    2: "🙂 Slightly",
    3: "😌 Moderately",
    4: "😄 Very Much",
    5: "🤩 Extremely"
}

user_responses = {}

# Loop through questions
for idx, row in df.iterrows():
    st.markdown(f"### **{row['ID']}. {row['Question']}**")

    # Slider replaced with radio buttons (for emojis)
    choice = st.radio(
        "How much would you enjoy this activity?",
        list(options.keys()),
        format_func=lambda x: options[x],
        key=row["ID"]
    )

    user_responses[row["ID"]] = choice
    st.write("---")

# Add scores to dataframe
df["Score"] = df["ID"].map(user_responses)

# Calculate RIASEC totals
scores = df.groupby("Dimension")["Score"].sum().to_dict()

st.subheader("📌 Your RIASEC Interest Scores")
st.write(scores)
