import os
from datetime import timedelta, timezone
from email.utils import parsedate_to_datetime

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API = {
    "환율": "https://v6.exchangerate-api.com/v6/{key}/latest/{base}",  # 🔌
}
KEY_NAME = "EXCHANGERATE_API_KEY"
KST = timezone(timedelta(hours=9))
CURRENCIES = {
    "KRW": "원 (KRW)",
    "USD": "미국 달러 (USD)",
    "EUR": "유로 (EUR)",
    "JPY": "일본 엔 (JPY)",
    "CNY": "중국 위안 (CNY)",
    "GBP": "영국 파운드 (GBP)",
    "AUD": "호주 달러 (AUD)",
    "CAD": "캐나다 달러 (CAD)",
}


@st.cache_data(ttl=3600)
def fetch_rates(api_key, base):
    url = API["환율"].format(key=api_key, base=base)
    try:
        res = requests.get(url, timeout=10)
    except requests.RequestException as e:
        # 예외 메시지에 주소(키 포함)가 들어갈 수 있어 종류만 반환
        return None, f"환율 요청에 실패했어요: {type(e).__name__}"
    if res.status_code != 200:
        return None, f"환율 API 오류 (상태 코드 {res.status_code})"
    data = res.json()
    if data.get("result") != "success":
        return None, "환율 API가 오류를 돌려줬어요. 키와 통화 코드를 확인해 주세요."
    return data, None


def to_kst(utc_text):
    return parsedate_to_datetime(utc_text).astimezone(KST).strftime("%Y-%m-%d %H:%M")


st.set_page_config(page_title="환율 계산기", page_icon="💱")
st.markdown(
    """
    <style>
    .stApp { background: #0B1F4B; color: #EAF1FF; }
    h1, h2, h3, label, p, span { color: #EAF1FF !important; }
    .result-box {
        background: #1E4DB7; border-left: 8px solid #FFD43B;
        border-radius: 12px; padding: 20px 24px; margin: 16px 0;
    }
    .result-box .big { font-size: 2.2rem; font-weight: 700; color: #FFD43B !important; }
    .result-box .small { color: #CFE0FF !important; font-size: 0.95rem; }
    div.stButton > button {
        background: #FFD43B; color: #0B1F4B; border: none; font-weight: 700;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("💱 환율 계산기")

api_key = os.getenv(KEY_NAME)
if not api_key:
    st.error(f".env에서 {KEY_NAME}를 찾지 못했어요.")
    st.stop()

col1, col2 = st.columns(2)
base = col1.selectbox("보내는 통화", list(CURRENCIES), format_func=CURRENCIES.get, index=1)
target = col2.selectbox("받는 통화", list(CURRENCIES), format_func=CURRENCIES.get, index=0)
amount = st.number_input("금액", min_value=0.0, value=1.0, step=1.0)

if st.button("새로고침"):
    fetch_rates.clear()

data, error = fetch_rates(api_key, base)
if error:
    st.error(error)
    st.stop()

rate = data["conversion_rates"].get(target)
if rate is None:
    st.error("선택한 통화의 환율 정보가 없어요.")
    st.stop()

st.markdown(
    f"""
    <div class="result-box">
        <div class="small">{amount:,.2f} {base} =</div>
        <div class="big">{amount * rate:,.2f} {target}</div>
        <div class="small">1 {base} = {rate:,.4f} {target}</div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.caption(f"기준 시각: {to_kst(data['time_last_update_utc'])} (한국 시간) · 무료 플랜은 하루 1회 갱신돼요.")
