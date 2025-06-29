import streamlit as st
import os
import random
from dotenv import load_dotenv
import google.generativeai as genai
import re

# Cấu hình giao diện
st.set_page_config(
    page_title="Premier League Chatbot",
    page_icon="epl_icon.png",  # Biểu tượng trang (favicon)
    layout="wide"
)

# Tải API key từ file .env
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Khởi tạo mô hình Gemini
model = genai.GenerativeModel("gemini-2.0-flash-lite")

# Từ khóa chào
greeting_keywords = ["hi", "hello", "hey", "who are you", "introduce", "your name", "xin chào", "bạn là ai"]

def is_greeting(question):
    q_lower = question.lower()
    return any(keyword in q_lower for keyword in greeting_keywords)

# Prompt nâng cao
def ask_epl_only(question):
    if is_greeting(question):
        return (
            "Xin chào! Tôi là trợ lý ảo chuyên về giải Ngoại hạng Anh (Premier League). "
            "Bạn có thể hỏi tôi về cầu thủ, câu lạc bộ, bảng xếp hạng, lịch sử giải đấu, "
            "kết quả, chuyển nhượng, thống kê và nhiều hơn nữa!"
        )

    prompt = f"""
Bạn là một trợ lý ảo thông minh, am hiểu sâu sắc về giải bóng đá Ngoại hạng Anh (English Premier League - EPL), cả quá khứ và hiện tại.

 Vai trò của bạn:
- Trả lời mọi câu hỏi liên quan đến giải Ngoại hạng Anh từ khi giải đấu được thành lập năm 1992 đến nay.
- Bao gồm: cầu thủ hiện tại và đã giải nghệ, huấn luyện viên, kết quả mùa trước, lịch thi đấu, bảng xếp hạng, thành tích CLB, lịch sử chuyển nhượng, phong độ, đội hình, sân vận động, số áo, bàn thắng, kỷ lục, sự kiện nổi bật, và các thống kê liên quan đến EPL.
- Có thể nói về các huyền thoại như Alan Shearer, Rooney, Henry, Drogba, Lampard, Gerrard, v.v.

 Ngôn ngữ:
- Trả lời bằng **chính ngôn ngữ** mà người dùng sử dụng (tiếng Việt hoặc tiếng Anh).
- Tránh dịch sang ngôn ngữ khác nếu không được yêu cầu.

 Phong cách trả lời:
- Tự nhiên, thân thiện, chuyên nghiệp.
- Tránh nhắc lại yêu cầu của người dùng.
- Nếu câu hỏi không hoàn toàn rõ ràng, hãy chủ động **suy đoán hợp lý** hoặc **hỏi lại một cách lịch sự**.
- Nếu câu hỏi không liên quan đến EPL, trả lời nhẹ nhàng: “Tôi chỉ chuyên về giải Ngoại hạng Anh, bạn vui lòng hỏi câu khác nhé.”

 Tránh:
- Không trả lời về các giải đấu khác (La Liga, Serie A, Champions League…) trừ khi có liên hệ với cầu thủ từng chơi ở EPL.
- Không đưa ra thông tin giả định, trừ khi người dùng yêu cầu rõ là “dự đoán” hoặc “tưởng tượng”.

Dưới đây là câu hỏi của người dùng, hãy trả lời đầy đủ, chi tiết, và đúng ngữ cảnh:

{question}
"""
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error: {e}"

# Lấy danh sách cầu thủ
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

# Khởi tạo session
if "correct_answer" not in st.session_state:
    st.session_state.correct_answer = random.choice(player_list)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Giao diện 2 cột
col1, col2 = st.columns([3, 1])

# ====== CỘT 1: CHATBOT =======
with col1:
    st.title("Premier League Chatbot")
    st.markdown("*Hỏi tôi về cầu thủ, câu lạc bộ, kết quả, lịch sử hoặc bất cứ điều gì liên quan đến Ngoại hạng Anh.*")

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

    # 👇 Tự động cuộn xuống dưới khi có tin nhắn mới
    st.markdown("""
        <script>
        var chatContainer = window.parent.document.querySelector('.main');
        chatContainer.scrollTo({top: chatContainer.scrollHeight, behavior: 'smooth'});
        </script>
    """, unsafe_allow_html=True)

# ====== CỘT 2: PLAYERDLE GAME =======
with col2:
    st.markdown("## 🎮 Playerdle")
    st.markdown(f"""
    **Đoán tên cầu thủ EPL:**  
    - Bạn có 6 lần thử.  
    - Mỗi chữ cái sẽ được đánh giá:  
        - 🟩 Đúng vị trí  
        - 🟨 Có trong tên, sai vị trí  
        - ❌ Không có trong tên  
    - Gợi ý: Tên cầu thủ có **{len(st.session_state.correct_answer)} chữ cái**
    """)

    if "guesses" not in st.session_state:
        st.session_state.guesses = []

    guess = st.text_input("🎯 Nhập tên cầu thủ (chữ thường, không dấu)")
    if guess and len(guess) == len(st.session_state.correct_answer) and guess not in st.session_state.guesses:
        st.session_state.guesses.append(guess)
    elif guess and len(guess) != len(st.session_state.correct_answer):
        st.warning(f"⚠️ Tên cầu thủ phải có {len(st.session_state.correct_answer)} chữ cái.")

    for idx, g in enumerate(st.session_state.guesses, start=1):
        feedback = []
        for i, c in enumerate(g):
            if i < len(st.session_state.correct_answer):
                if c == st.session_state.correct_answer[i]:
                    feedback.append(f"[🟩{c.upper()}]")
                elif c in st.session_state.correct_answer:
                    feedback.append(f"[🟨{c.upper()}]")
                else:
                    feedback.append(f"[❌{c.upper()}]")
        st.write(f"Lần {idx}: {''.join(feedback)}")

    if st.session_state.guesses and st.session_state.guesses[-1] == st.session_state.correct_answer:
        st.success("🎉 Chính xác! Bạn đã đoán đúng!")
        if st.button("🔄 Chơi lại"):
            st.session_state.guesses = []
            st.session_state.correct_answer = random.choice(player_list)
    elif len(st.session_state.guesses) >= 6:
        st.error(f"❌ Hết lượt! Đáp án đúng là: **{st.session_state.correct_answer.title()}**")
        if st.button("🔄 Chơi lại"):
            st.session_state.guesses = []
            st.session_state.correct_answer = random.choice(player_list)
