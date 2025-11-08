
import time
import streamlit as st
import pyrebase
import firebase_admin
import requests
from firebase_admin import credentials, firestore
from firebase_admin import auth as admin_auth
from collections import deque
from datetime import datetime, timezone
from ollama import Client
from streamlit_extras.stylable_container import stylable_container

# ----------------------------------------
# STREAMLIT BASE
# ----------------------------------------
st.set_page_config(page_title="MiniTravelLab", page_icon="🌍")
MODEL = "llama3.2:1b"

# ✅ UPDATE THIS URL AFTER ngrok RUNS
client = Client(
    host="YOUR_NGROK_URL_HERE"  
)

# ----------------------------------------
# ✅ FIXED FIREBASE LOGIN
# ----------------------------------------
API_KEY = st.secrets["firebase_client"]["apiKey"]

def fb_sign_in(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    r = requests.post(url, json=payload)
    if r.status_code != 200:
        try:
            msg = r.json()["error"]["message"]
        except:
            msg = "UNKNOWN_ERROR"
        raise RuntimeError(msg)
    return r.json()

def fb_sign_up(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={API_KEY}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    r = requests.post(url, json=payload)
    if r.status_code != 200:
        try:
            msg = r.json()["error"]["message"]
        except:
            msg = "UNKNOWN_ERROR"
        raise RuntimeError(msg)
    return r.json()


# ----------------------------------------
# FIREBASE INIT
# ----------------------------------------
@st.cache_resource
def get_firebase_clients():
    firebase_cfg = st.secrets["firebase_client"]
    firebase_app = pyrebase.initialize_app(firebase_cfg)
    auth = firebase_app.auth()

    if not firebase_admin._apps:
        cred = credentials.Certificate(dict(st.secrets["firebase_admin"]))
        firebase_admin.initialize_app(cred)

    db = firestore.client()
    return auth, db

auth, db = get_firebase_clients()


# ----------------------------------------
# HISTORY
# ----------------------------------------
def save_itinerary(uid, itinerary):
    doc = {
        "itinerary": itinerary,
        "ts": datetime.now(timezone.utc)
    }
    db.collection("itineraries").document(uid).collection("plans").add(doc)

def load_last_itineraries(uid, limit=5):
    q = (db.collection("itineraries").document(uid)
         .collection("plans")
         .order_by("ts", direction=firestore.Query.DESCENDING)
         .limit(limit))
    docs = list(q.stream())
    return [d.to_dict() for d in docs]


# ----------------------------------------
# ITINERARY GENERATION
# ----------------------------------------
def generate_itinerary(origin, destination, start, end, interests, pace):
    prompt = f"""
Create a detailed day-by-day travel itinerary from {origin} to {destination}
between {start} and {end}.

Interests: {', '.join(interests)}
Pace: {pace}

Provide structured itinerary output.
"""
    try:
        response = client.chat(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        return response["message"]["content"]
    except Exception as e:
        return f"Ollama error: {e}"


# ----------------------------------------
# SESSION
# ----------------------------------------
if "user" not in st.session_state:
    st.session_state.user = None

# ----------------------------------------
# LOGIN
# ----------------------------------------
def login_form():
    st.subheader("Đăng nhập")

    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Mật khẩu", type="password")

        col1, col2 = st.columns(2)
        login_btn = col1.form_submit_button("Đăng nhập")
        signup_btn = col2.form_submit_button("Chưa có tài khoản? Đăng ký")

    if signup_btn:
        st.session_state["show_signup"] = True
        st.session_state["show_login"] = False
        st.rerun()

    if login_btn:
        try:
            res = fb_sign_in(email, password)

            st.session_state.user = {
                "email": res["email"],
                "uid": res["localId"],
                "idToken": res["idToken"]
            }
            st.success("Đăng nhập thành công!")
            st.rerun()

        except Exception as e:
            st.error(f"Đăng nhập thất bại: {e}")


# ----------------------------------------
# SIGNUP
# ----------------------------------------
def signup_form():
    st.subheader("Tạo tài khoản")

    with st.form("signup_form"):
        email = st.text_input("Email mới")
        password = st.text_input("Mật khẩu (≥6 ký tự)", type="password")

        col1, col2 = st.columns(2)
        signup_btn = col1.form_submit_button("Đăng ký")
        login_btn = col2.form_submit_button("Đã có tài khoản? Đăng nhập")

    if login_btn:
        st.session_state["show_signup"] = False
        st.session_state["show_login"] = True
        st.rerun()

    if signup_btn:
        try:
            fb_sign_up(email, password)
            st.success("Tạo tài khoản thành công! Vui lòng đăng nhập.")
            time.sleep(1)
            st.session_state["show_signup"] = False
            st.session_state["show_login"] = True
            st.rerun()
        except Exception as e:
            st.error(f"Đăng ký thất bại: {e}")


# ----------------------------------------
# MAIN UI
# ----------------------------------------
st.title("🌍 MiniTravelLab — Itinerary AI")

if "show_login" not in st.session_state:
    st.session_state["show_login"] = True
if "show_signup" not in st.session_state:
    st.session_state["show_signup"] = False

if st.session_state.user:

    st.success(f"Đang đăng nhập: {st.session_state.user['email']}")

    if st.button("Đăng xuất"):
        st.session_state.user = None
        st.rerun()

    st.divider()
    st.header("🧭 Tạo lịch trình du lịch AI")

    with st.form("itin_form"):
        origin = st.text_input("Điểm khởi hành")
        destination = st.text_input("Điểm đến")

        col1, col2 = st.columns(2)
        start_date = col1.date_input("Ngày bắt đầu")
        end_date = col2.date_input("Ngày kết thúc")

        interests = st.multiselect("Sở thích",
                                   ["food", "museums", "nature", "nightlife", "shopping"])

        pace = st.selectbox("Tốc độ chuyến đi",
                            ["relaxed", "normal", "tight"])

        submit = st.form_submit_button("Tạo lịch trình")

    if submit:
        itinerary = generate_itinerary(origin, destination, start_date, end_date, interests, pace)
        st.markdown("### ✅ Lịch trình được tạo:")
        st.markdown(itinerary)

        save_itinerary(st.session_state.user["uid"], itinerary)

    st.divider()
    st.subheader("📜 Lịch sử lịch trình gần đây")

    history = load_last_itineraries(st.session_state.user["uid"])
    for item in history:
        with st.expander("Xem lịch trình"):
            st.markdown(item["itinerary"])

else:
    if st.session_state["show_signup"]:
        signup_form()
    else:
        login_form()

