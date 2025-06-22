import streamlit as st
import os
import random
from dotenv import load_dotenv
import google.generativeai as genai

st.set_page_config(
    page_title="Premier League Chatbot",
    page_icon="epl_icon.png",  # Favicon
    layout="wide"
)

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel("gemini-2.0-flash-lite")

greeting_keywords = ["hi", "hello", "chào", "hey", "bạn là ai", "giới thiệu", "bạn tên gì"]

def is_greeting(question):
    q_lower = question.lower()
    return any(keyword in q_lower for keyword in greeting_keywords)

def ask_epl_only(question):
    if is_greeting(question):
        return (
            "Xin chào! Tôi là chatbot chuyên về Premier League (Ngoại hạng Anh). "
            "Tôi có thể giúp bạn với thông tin về các cầu thủ, câu lạc bộ, "
            "lịch thi đấu, kết quả, bảng xếp hạng hoặc chuyển nhượng EPL. "
            "Hãy đặt câu hỏi nhé!"
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

# Lấy danh sách cầu thủ EPL tự động từ AI
@st.cache_data(show_spinner=False)
def get_epl_players():
    prompt = "List 50 famous current Premier League players. Only return lowercase names without accents, separated by commas."
    try:
        response = model.generate_content(prompt)
        names = response.text.strip().lower().replace('\n', '').split(',')
        return [name.strip() for name in names if name.strip()]
    except:
        return ["salah", "haaland", "rashford", "son", "saka", "foden", "rodri", "odegaard"]

# Dùng AI sinh danh sách cầu thủ
player_list = get_epl_players()

# Khởi tạo correct_answer ngẫu nhiên mỗi lần load
if "correct_answer" not in st.session_state:
    st.session_state.correct_answer = random.choice(player_list)

# Bố cục 2 cột: Chatbot | Playerdle
col1, col2 = st.columns([3, 1])

with col1:
    st.title("Premier League Chatbot")
    st.markdown("*Hỏi tôi về cầu thủ, CLB, kết quả hoặc thông tin liên quan đến Premier League.*")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    question = st.chat_input("Nhập câu hỏi của bạn...")

    if question:
        st.session_state.messages.append({"role": "user", "text": question})

        with st.spinner("Đang suy nghĩ..."):
            answer = ask_epl_only(question)
            st.session_state.messages.append({"role": "bot", "text": answer})

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.markdown(msg["text"])
        else:
            with st.chat_message("bot", avatar="Logo.png"):
                st.markdown(msg["text"])

with col2:
    st.markdown("## 🎮 Playerdle")
    st.markdown(f"""
    **Đoán tên cầu thủ EPL:**
    - Bạn có 6 lượt đoán.
    - Mỗi chữ được đánh giá:
        - 🟩 Đúng vị trí
        - 🟨 Đúng chữ, sai vị trí
        - ❌ Sai hoàn toàn
    - Gợi ý: Tên cầu thủ có **{len(st.session_state.correct_answer)} chữ cái**
    """)

    if "guesses" not in st.session_state:
        st.session_state.guesses = []

    guess = st.text_input("🎯 Nhập tên cầu thủ (viết thường, không dấu)")
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
        st.success("🎉 Chính xác! Bạn đoán đúng rồi!")
        if st.button("🔄 Chơi lại"):
            st.session_state.guesses = []
            st.session_state.correct_answer = random.choice(player_list)
    elif len(st.session_state.guesses) >= 6:
        st.error(f"❌ Hết lượt! Đáp án là: {st.session_state.correct_answer.title()}")
        if st.button("🔄 Chơi lại"):
            st.session_state.guesses = []
            st.session_state.correct_answer = random.choice(player_list)


