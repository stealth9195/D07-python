import os

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

KEY_NAMES = ["OPENWEATHER_API_KEY", "OPENWEATHERMAP_API_KEY", "OPENWEATHER_KEY", "WEATHER_API_KEY"]
URL = "https://api.openweathermap.org/data/2.5/weather"


def find_api_key():
    for name in KEY_NAMES:
        value = os.getenv(name)
        if value:
            return value
    return None


@st.cache_data(ttl=300)
def fetch_weather(api_key):
    params = {"q": "Seoul,KR", "appid": api_key, "units": "metric", "lang": "kr"}
    try:
        res = requests.get(URL, params=params, timeout=10)
    except requests.RequestException as e:
        # 예외 메시지에 URL(키 포함)이 들어갈 수 있어 종류만 반환
        return None, f"요청에 실패했어요: {type(e).__name__}"
    if res.status_code != 200:
        return None, f"API 오류 (상태 코드 {res.status_code})"
    return res.json(), None


st.title("서울의 현재 날씨")

api_key = find_api_key()
if not api_key:
    st.error(".env에서 API 키를 찾지 못했어요. 확인한 이름: " + ", ".join(KEY_NAMES))
    st.stop()

if st.button("새로고침"):
    fetch_weather.clear()

data, error = fetch_weather(api_key)
if error:
    st.error(error)
    st.stop()

st.subheader(data["weather"][0]["description"])
col1, col2, col3 = st.columns(3)
col1.metric("기온", f"{data['main']['temp']}°C")
col2.metric("체감 온도", f"{data['main']['feels_like']}°C")
col3.metric("습도", f"{data['main']['humidity']}%")
