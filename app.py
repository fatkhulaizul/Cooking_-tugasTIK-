import streamlit as st
import google.generativeai as genai
import os

# ==============================================================================
# PENGATURAN API KEY DAN MODEL
# ==============================================================================
# Untuk GitHub, API Key sebaiknya disimpan di Secrets.
# Jangan pernah hardcode API Key Anda di dalam kode yang akan diunggah ke GitHub.
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("API Key tidak ditemukan. Pastikan Anda telah menyimpan GEMINI_API_KEY di Streamlit Secrets.")
    st.stop()

MODEL_NAME = 'gemini-1.5-flash'

# ==============================================================================
# KONTEKS AWAL CHATBOT
# ==============================================================================
INITIAL_CHATBOT_CONTEXT = [
    {
        "role": "user",
        "parts": ["Kamu adalah Koki yang sangat ahli dibidangnya. Berikan user berbagai macam resep-resep makanan yang diminta!. Jawaban singkat dan faktual. Tolak pertanyaan selain yang berhubungan tentang masakan ."]
    },
    {
        "role": "model",
        "parts": ["Baik! Saya akan memberikan resep yang Anda inginkan."]
    }
]

# ==============================================================================
# FUNGSI UTAMA UNTUK MENGELOLA SESI CHAT
# ==============================================================================
# Mengatur konfigurasi API
genai.configure(api_key=API_KEY)

@st.cache_resource(show_spinner=False)
def get_model():
    """Menginisialisasi model Gemini."""
    try:
        model = genai.GenerativeModel(
            MODEL_NAME,
            generation_config=genai.types.GenerationConfig(
                temperature=0.4,
                max_output_tokens=500
            )
        )
        return model
    except Exception as e:
        st.error(f"Kesalahan saat inisialisasi model '{MODEL_NAME}': {e}")
        st.stop()

model = get_model()

# Mengatur judul halaman dan ikon
st.set_page_config(
    page_title="Chef Gemini - Resep Instan",
    page_icon="🍳"
)

st.title("👨‍🍳 Chef Gemini")
st.markdown("Halo! Saya Chef Gemini, asisten pribadi Anda untuk resep masakan. Tanyakan saja resep apa yang Anda inginkan!")

# Inisialisasi riwayat chat di Streamlit Session State
# Ini penting agar riwayat chat tidak hilang setiap kali ada interaksi.
if "chat_history" not in st.session_state:
    st.session_state.chat_history = INITIAL_CHATBOT_CONTEXT

if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=st.session_state.chat_history)

# Menampilkan riwayat chat
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["parts"][0])

# Menerima input dari pengguna
if user_input := st.chat_input("Tulis resep yang Anda cari..."):
    # Menambahkan input user ke riwayat chat
    st.session_state.chat_history.append({"role": "user", "parts": [user_input]})
    
    # Menampilkan pesan user di UI
    with st.chat_message("user"):
        st.markdown(user_input)

    # Mengirim input ke model dan mendapatkan respons
    with st.chat_message("assistant"):
        with st.spinner("Sedang memproses..."):
            try:
                response = st.session_state.chat_session.send_message(user_input, request_options={"timeout": 60})
                
                if response and response.text:
                    st.markdown(response.text)
                    # Menambahkan respons model ke riwayat chat
                    st.session_state.chat_history.append({"role": "model", "parts": [response.text]})
                else:
                    st.markdown("Maaf, saya tidak bisa memberikan balasan.")
            except Exception as e:
                st.markdown(f"Maaf, terjadi kesalahan saat berkomunikasi dengan Gemini: {e}")
