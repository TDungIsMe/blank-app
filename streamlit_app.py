import streamlit as st
import os
import random
from dotenv import load_dotenv
import google.generativeai as genai
import re

st.set_page_config(
    page_title="Premier League Chatbot",
    page_icon="epl_icon.png",  # Favicon
    layout="wide"
)

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel("gemini-2.0-flash-lite")

greeting_keywords = ["hi", "hello", "hey", "who are you", "introduce", "your name"]

def is_greeting(question):
    q_lower = question.lower()
    return any(keyword in q_lower for keyword in greeting_keywords)

def ask_epl_only(question):
    if is_greeting(question):
        return (
            "Hello! I'm a chatbot specialized in the Premier League. "
            "I can help you with information about players, clubs, "
            "fixtures, results, standings, or EPL transfers. "
            "Ask me anything!"
        )

    prompt = f"""
You are a helpful assistant that ONLY answers questions related to the English Premier League (EPL).

If the user's question is about EPL players, clubs, results, fixtures, standings, or EPL-related transfers/stats — please answer helpfully and informatively.

If the question is NOT related to the EPL, just say:
"Sorry, I only answer questions related to the English Premier League (EPL)."

User's question: {question}
"""
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error: {e}"

@st.cache_data(show_spinner=False)
def get_epl_players():
    prompt = "List 50 current Premier League players. Return only lowercase names without accents, separated by commas. Do not explain."
    try:
        response = model.generate_content(prompt)
        raw_text = response.text.strip().lower()
        if ':' in raw_text:
            raw_text = raw_text.split(':')[-1]
        names = raw_text.replace('\n', '').split(',')
        clean_names = []
        for name in names:
            name = name.strip()
            if 3 <= len(name) <= 20 and re.match("^[a-z ]+$", name):
                clean_names.append(name)
        return clean_names[:40]
    except:
        return ["salah", "haaland", "rashford", "son", "saka", "foden", "rodri", "odegaard"]

player_list = get_epl_players()

if "correct_answer" not in st.session_state:
    st.session_state.correct_answer = random.choice(player_list)

col1, col2 = st.columns([3, 1])

with col1:
    st.title("Premier League Chatbot")
    st.markdown("*Ask me about players, clubs, results or anything related to the Premier League.*")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.markdown(msg["text"])
        else:
            with st.chat_message("bot", avatar="Logo.png"):
                st.markdown(msg["text"])

    question = st.chat_input("Type your question...")

    if question:
        st.session_state.messages.append({"role": "user", "text": question})

        with st.spinner("Thinking..."):
            answer = ask_epl_only(question)
            st.session_state.messages.append({"role": "bot", "text": answer})

with col2:
    st.markdown("## 🎮 Playerdle")
    st.markdown(f"""
    **Guess the EPL Player Name:**
    - You have 6 attempts.
    - Each character will be evaluated:
        - 🟩 Correct position
        - 🟨 Correct letter, wrong position
        - ❌ Wrong letter
    - Hint: The player name has **{len(st.session_state.correct_answer)} letters**
    """)

    if "guesses" not in st.session_state:
        st.session_state.guesses = []

    guess = st.text_input("🎯 Enter player name (lowercase, no accents)")
    if guess and guess not in st.session_state.guesses:
        st.session_state.guesses.append(guess)

    for g in st.session_state.guesses:
        feedback = []
        for i, c in enumerate(g):
            if i < len(st.session_state.correct_answer):
                if c == st.session_state.correct_answer[i]:
                    feedback.append(f"[🟩{c.upper()}]")
                elif c in st.session_state.correct_answer:
                    feedback.append(f"[🟨{c.upper()}]")
                else:
                    feedback.append(f"[❌{c.upper()}]")
        st.write("".join(feedback))

    if st.session_state.guesses and st.session_state.guesses[-1] == st.session_state.correct_answer:
        st.success("🎉 Correct! You guessed it!")
        if st.button("🔄 Play again"):
            st.session_state.guesses = []
            st.session_state.correct_answer = random.choice(player_list)
    elif len(st.session_state.guesses) >= 6:
        st.error(f"❌ Out of attempts! The correct answer was: {st.session_state.correct_answer.title()}")
        if st.button("🔄 Play again"):
            st.session_state.guesses = []
            st.session_state.correct_answer = random.choice(player_list)
