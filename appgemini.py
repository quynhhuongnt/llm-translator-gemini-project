import streamlit as st
from PIL import Image
from google import genai
from dotenv import load_dotenv
from google.genai import types
import os
import io
from langsmith import traceable


# =========================================================
# 1. CẤU HÌNH HỆ THỐNG & API KEYS
# =========================================================

# Nạp biến môi trường từ file .env (khi chạy local) 
# Hoặc từ Secrets (khi chạy trên Streamlit Cloud)
load_dotenv() 

# Lấy Key từ môi trường hệ thống
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")

# LangSmith
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGSMITH_API_KEY"] = LANGSMITH_API_KEY
os.environ["LANGSMITH_PROJECT"] = "Translator-Project-Deep-Learning"

#Gemini Client
try:
    # Sử dụng biến GEMINI_API_KEY đã lấy ở trên
    client = genai.Client(api_key=GEMINI_API_KEY)
    MODEL_NAME = "models/gemini-2.0-flash-lite"
except Exception as e:
    st.error(f"Lỗi khởi tạo API: {e}")

# =========================================================
# 2. HÀM XỬ LÝ LOGIC (CÓ TRACING)
# =========================================================

@traceable(name="AI_Translation_Engine")
def translate_engine(contents):
    """Hàm trung tâm gọi Gemini API và log dữ liệu lên LangSmith"""
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=contents
        )
        return response.text
    except Exception as e:
        if "429" in str(e):
            return "⚠️ LỖI QUOTA (429): Bạn đã hết lượt dùng miễn phí. Vui lòng đợi 60s."
        return f"❌ LỖI: {str(e)}"

# =========================================================
# 3. GIAO DIỆN TÙY CHỈNH (CSS)
# =========================================================

st.set_page_config(page_title="Deep Learning Translator", layout="wide", page_icon="🇬🇧🇻🇳")

st.markdown("""
<style>
    .stTextArea textarea { font-size: 16px; height: 300px; font-family: sans-serif; }
    .stButton button { 
        background-color: #1a73e8; color: white; font-size: 16px; 
        border-radius: 8px; padding: 0.5rem 1rem; width: 100%; font-weight: bold;
    }
    .stButton button:hover { background-color: #1557b0; color: white; }
    .result-box { 
        border: 1px solid #d3d3d3; border-radius: 0.5rem; padding: 1rem; height: 300px;              
        background-color: #f0f2f6; color: #31333F; overflow-y: auto;
        white-space: pre-wrap; font-family: sans-serif; font-size: 16px;
    }
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .lang-header { font-weight: bold; font-size: 18px; margin-bottom: 10px; display: block; color: #1a73e8; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 4. GIAO DIỆN ỨNG DỤNG (UI)
# =========================================================

st.title(" ỨNG DỤNG DỊCH ĐA PHƯƠNG THỨC ANH - VIỆT SỬ DỤNG LLM ")
st.info("Môn: Kĩ thuật học sâu | SV: Ngô Thị Quỳnh Hương | MSV: 99048 | Tech: Gemini 2.0 & LangSmith")

tab_text, tab_image, tab_doc = st.tabs(["🔤 Văn Bản", "📸 Hình Ảnh", "📂 Tài Liệu"])

# --- TAB 1: DỊCH VĂN BẢN ---
with tab_text:
    st.write("") 
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<span class="lang-header">TIẾNG ANH</span>', unsafe_allow_html=True)
        text_input = st.text_area("Input", placeholder="Nhập văn bản tiếng Anh...", label_visibility="collapsed", key="txt_in")
    with col2:
        st.markdown('<span class="lang-header">TIẾNG VIỆT</span>', unsafe_allow_html=True)
        res_txt = st.empty()
        res_txt.markdown('<div class="result-box">Kết quả dịch sẽ hiển thị tại đây...</div>', unsafe_allow_html=True)

    if st.button("DỊCH VĂN BẢN", key="btn_text"):
        if text_input.strip():
            with st.spinner("Đang dịch & Tracing..."):
                ans = translate_engine(f"Dịch văn bản sau sang tiếng Việt: {text_input}")
                res_txt.markdown(f'<div class="result-box">{ans}</div>', unsafe_allow_html=True)
        else:
            st.warning("Vui lòng nhập văn bản!")

# --- TAB 2: DỊCH HÌNH ẢNH ---
with tab_image:
    st.write("")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<span class="lang-header">TẢI ẢNH LÊN</span>', unsafe_allow_html=True)
        up_img = st.file_uploader("Upload Image", type=['png', 'jpg', 'jpeg'], label_visibility="collapsed")
        if up_img: st.image(Image.open(up_img), use_container_width=True)
    with col2:
        st.markdown('<span class="lang-header">KẾT QUẢ DỊCH</span>', unsafe_allow_html=True)
        res_img = st.empty()
        res_img.markdown('<div class="result-box">Đang đợi ảnh...</div>', unsafe_allow_html=True)

    if st.button("QUÉT & DỊCH ", key="btn_img"):
        if up_img:
            with st.spinner("Đang phân tích Vision..."):
                img_data = Image.open(up_img)
                ans = translate_engine(["Trích xuất và dịch toàn bộ văn bản trong ảnh sang tiếng Việt", img_data])
                res_img.markdown(f'<div class="result-box">{ans}</div>', unsafe_allow_html=True)

# --- TAB 3: DỊCH TÀI LIỆU ---
with tab_doc:
    st.write("")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<span class="lang-header">TẢI FILE (PDF/TXT)</span>', unsafe_allow_html=True)
        up_doc = st.file_uploader("Upload Doc", type=['pdf', 'txt'], label_visibility="collapsed")
    with col2:
        st.markdown('<span class="lang-header">NỘI DUNG DỊCH</span>', unsafe_allow_html=True)
        res_doc = st.empty()
        res_doc.markdown('<div class="result-box">Đang đợi tài liệu...</div>', unsafe_allow_html=True)

    if st.button("DỊCH TOÀN BỘ TÀI LIỆU", key="btn_doc"):
        if up_doc:
            with st.spinner("Đang xử lý tài liệu đa trang..."):
                bytes_data = up_doc.read()
                ans = translate_engine([
                    types.Part.from_bytes(data=bytes_data, mime_type=up_doc.type),
                    "Dịch toàn bộ tài liệu này sang tiếng Việt."
                ])
                res_doc.markdown(f'<div class="result-box">{ans}</div>', unsafe_allow_html=True)
                st.download_button("Tải xuống bản dịch (.txt)", ans, file_name="translated.txt")