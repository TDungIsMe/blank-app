import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel("gemini-2.0-flash-lite")

def ask_epl_only(question):
    prompt = f"""
You are a strict assistant that only answers questions related to the English Premier League (EPL).

You must refuse to answer any question that is not related to the EPL — including other football leagues, history, politics, science, or general knowledge.

If the question is not about EPL players, clubs, results, fixtures, standings, or EPL-related transfers/stats, respond with:

"Sorry, I only answer questions related to the English Premier League (EPL)."

User's question: {question}
"""
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error: {e}"

st.set_page_config(page_title="Premier League Chatbot", layout="centered")
st.title("Premier League Chatbot")
st.markdown("This assistant only answers questions about Premier League players, clubs, results and stats.")

if "messages" not in st.session_state:
    st.session_state.messages = []

question = st.chat_input("Enter your question...")

if question:
    st.session_state.messages.append({"role": "user", "text": question})

    with st.spinner("Thinking..."):
        answer = ask_epl_only(question)
        st.session_state.messages.append({"role": "bot", "text": answer})

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["text"])

