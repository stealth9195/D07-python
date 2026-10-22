import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

load_dotenv()

KEY_NAME = "OPENAI_API_KEY"
MODEL = "gpt-4o-mini"
SYSTEM_PROMPT = "너는 친절한 챗봇이야. 한국어로 간결하게 답해줘."

st.set_page_config(page_title="챗봇", page_icon="💬")
st.title("💬 챗봇")

api_key = os.getenv(KEY_NAME)
if not api_key:
    st.error(f".env에서 {KEY_NAME}를 찾지 못했어요.")
    st.stop()

client = OpenAI(api_key=api_key)

if "messages" not in st.session_state:
    st.session_state.messages = []

if st.sidebar.button("대화 지우기"):
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("메시지를 입력하세요"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            stream = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.messages,
                stream=True,
            )
            reply = st.write_stream(
                chunk.choices[0].delta.content or ""
                for chunk in stream
                if chunk.choices
            )
        except OpenAIError as e:
            # 오류 메시지에 키 일부가 들어갈 수 있어 종류만 출력
            reply = f"답변을 받지 못했어요: {type(e).__name__}"
            st.error(reply)
            st.session_state.messages.pop()
            st.stop()

    st.session_state.messages.append({"role": "assistant", "content": reply})
