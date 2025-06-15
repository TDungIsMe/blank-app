import streamlit as st
import os
import pandas as pd
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel("gemini-2.0-flash-lite")

def extract_player_name(question):
    prompt = f"""
    You are an assistant for English Premier League. Extract the football player's name from the question below. 
    
    Question: "{question}"
    
    If the name is found, return it. If not, return "None".
    """
    response = model.generate_content(prompt)
    return response.text.strip()

if "messages" not in st.session_state:
    st.session_state.messages = []

st.set_page_config(page_title="Chatbot - Premier League", layout="centered")
st.title("Premier League Chatbot")
st.markdown("Hỏi về cầu thủ, đội bóng, kết quả")

question = st.chat_input("Nhập câu hỏi...")

if question:
    st.session_state.messages.append({"role": "user", "text": question})

    with st.spinner("Đang hỏi Gemini..."):
        response = model.generate_content(question)
        answer = response.text.strip()
        st.session_state.messages.append({"role": "bot", "text": answer})

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message("user").markdown(msg["text"])
    else:
        st.chat_message("assistant").markdown(msg["text"])

