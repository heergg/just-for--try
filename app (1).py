import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------------
# Load CSVs
# ------------------------
try:
    df = pd.read_csv("riasec_30_questions.csv")
    meanings_df = pd.read_csv("riasec_meanings.csv")  # Fixed typo
except FileNotFoundError:
    st.error("❌ One of the CSV files is missing. Please place 'riasec_30_questions.csv' and 'riasec_meanings.csv' in the same folder.")
    st.stop()

st.set_page_config(page_title="RIASEC Test", layout="wide")

st.title("RIASEC Interest Test 🎯")
st.write("Rate each activity based on **how much you would enjoy doing it**.")

# ------------------------
# Emoji Options
# ------------------------
options = {
    1: "😐 Not at all",
    2: "🙂 Slightly",
    3: "😌 Moderately",
    4: "😄 Very Much",
    5: "🤩 Extremely"
}

# ------------------------
# Initialize session state
# ------------------------
if "index" not in st.session_state:
    st.session_state.index = 0
if "responses" not in st.session_state:
    st.session_state.responses = {}

# ------------------------
# Next question function
# ------------------------
def next_question():
    st.session_state.responses[st.session_state.index] = st.session_state[f"q_{st.session_state.index}"]
    st.session_state.index += 1

# ------------------------
# Test Completed: Show Dashboard
# ------------------------
if st.session_state.index >= len(df):
    df["Score"] = df["ID"].map(st.session_state.responses)
    scores = df.groupby("Dimension")["Score"].sum().to_dict()

    st.success("🎉 You have completed the RIASEC Test!")

    # ------------------------
    # Top 3 Interests + Meanings
    # ------------------------
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top3 = [d for d, _ in sorted_scores[:3]]

    st.subheader("🏆 Top 3 Interests")
    for dim in top3:
        meaning = meanings_df.loc[meanings_df["Dimension"] == dim, "Meaning"].values[0]
        st.markdown(f"- **{dim}** → {meaning}  (Score: {scores[dim]})")

    st.markdown("---")

    # ------------------------
    # Bar Chart
    # ------------------------
    st.subheader("📈 RIASEC Scores Overview")
    scores_df = pd.DataFrame(list(scores.items()), columns=["Dimension", "Score"])
    fig = px.bar(
        scores_df,
        x="Dimension",
        y="Score",
        text="Score",
        range_y=[0, 30],
        color="Score",
        color_continuous_scale="Viridis"
    )
    fig.update_layout(yaxis_title="Score", xaxis_title="Dimension", showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ------------------------
    # Radar Chart
    # ------------------------
    st.subheader("🎯 Radar Chart")
    fig2 = px.line_polar(
        scores_df,
        r="Score",
        theta="Dimension",
        line_close=True,
        markers=True
    )
    fig2.update_traces(fill='toself')
    st.plotly_chart(fig2, use_container_width=True)

    # ------------------------
    # Detailed Scores Table
    # ------------------------
    st.subheader("📋 Detailed Scores")
    st.dataframe(scores_df)

# ------------------------
# Test in Progress: Show current question
# ------------------------
else:
    idx = st.session_state.index
    row = df.iloc[idx]

    # Progress
    st.progress((idx+1)/len(df))
    st.markdown(f"**Question {idx+1} of {len(df)}**")

    st.markdown(f"### {row['Question']}")
    st.radio(
        "How much would you enjoy this activity?",
        list(options.keys()),
        format_func=lambda x: options[x],
        key=f"q_{idx}"
    )

    st.button("Next ➡️", on_click=next_question)


