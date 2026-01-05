import streamlit as st
from PIL import Image
from google import genai
from dotenv import load_dotenv
from google.genai import types
import os
import io
import time
import tempfile
from pypdf import PdfReader
from langsmith import traceable

from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4

# 1. CẤU HÌNH HỆ THỐNG & API KEYS 
 
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")

os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGSMITH_API_KEY"] = LANGSMITH_API_KEY
os.environ["LANGSMITH_PROJECT"] = "Translator-Project-Deep-Learning"

client = genai.Client(api_key=GEMINI_API_KEY)
MODEL_NAME = "models/gemini-2.0-flash-lite"

PROGRESS_FILE = "progress.txt"

 
# 2. ENGINE CHUNG (TAB 1 & TAB 2)
 
@traceable(name="AI_Translation_Engine")
def translate_engine(contents, temperature=0.2, max_tokens=2048):
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=contents,
        config=types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
            top_p=0.95,
        )
    )
    return response.text

 
# 3. PDF ENGINE (TAB 3)
 
@traceable(name="PDF_Page_Translation")
def dich_trang_pdf(text, page_number, system_prompt, temperature, max_tokens, max_retry=5):
    prompt = f"""
{system_prompt}

--- TRANG {page_number} ---
{text}
"""
    for attempt in range(max_retry):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens
                )
            )
            return response.text
        except Exception as e:
            if "429" in str(e):
                wait_time = 10 * (attempt + 1)
                st.warning(f" Hết quota, đợi {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise e
    raise RuntimeError(" Không thể dịch do hết quota.")

def  tai_tien_do():
    if not os.path.exists(PROGRESS_FILE):
        return 0, []
    with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    return int(lines[0].strip()), lines[1:]

def luu_tien_do(page_number, trang_da_dich):
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        f.write(str(page_number) + "\n")
        f.writelines(trang_da_dich)

def xuat_pdf_tieng_viet(text):
    pdfmetrics.registerFont(TTFont("DejaVu", "DejaVuSans.ttf"))
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="VN",
        fontName="DejaVu",
        fontSize=11,
        leading=14
    ))
    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    doc = SimpleDocTemplate(temp_pdf.name, pagesize=A4)
    story = [Paragraph(line, styles["VN"]) for line in text.split("\n")]
    doc.build(story)
    return temp_pdf.name

 
# 4. UI + SIDEBAR + CSS 
 
st.set_page_config(page_title="Deep Learning Translator", layout="wide", page_icon="🇬🇧🇻🇳")

with st.sidebar:
    st.header(" Cấu hình Model")
    temp_val = st.slider("Temperature ", 0.0, 1.0, 0.2, 0.1)
    max_token_val = st.number_input("Max Output Tokens", 100, 8192, 2048)
    st.divider()
    system_prompt = st.text_area(
        "Yêu cầu :",
        value="Translate the following English text into Vietnamese.Keep the meaning accurate.Do not add explanations or comments."
    )

st.markdown("""
<style>
    .stTextArea textarea { font-size: 16px; height: 300px; font-family: sans-serif; }
    .stButton button { 
        background-color: #1a73e8; color: white; font-size: 16px; 
        border-radius: 8px; padding: 0.5rem 1rem; width: 100%; font-weight: bold;
    }
    .result-box { 
        border: 1px solid #d3d3d3; border-radius: 0.5rem; padding: 1rem; height: 300px;              
        background-color: #f0f2f6; color: #31333F; overflow-y: auto;
        white-space: pre-wrap; font-family: sans-serif; font-size: 16px;
    }
    .lang-header { font-weight: bold; font-size: 18px; margin-bottom: 10px; display: block; color: #1a73e8; }
</style>
""", unsafe_allow_html=True)

st.title(" ỨNG DỤNG DỊCH ĐA PHƯƠNG THỨC ANH - VIỆT ")
st.caption("Môn: Kỹ thuật học sâu và ứng dụng | SV: Ngô Thị Quỳnh Hương | MSV: 99048")

tab_text, tab_image, tab_doc = st.tabs([" VĂN BẢN ", " HÌNH ẢNH ", "TÀI LIỆU "])

 
# TAB 1 – VĂN BẢN
 
with tab_text:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<span class="lang-header">VĂN BẢN CẦN DỊCH</span>', unsafe_allow_html=True)
        text_input = st.text_area("Input", label_visibility="collapsed")
    with col2:
        st.markdown('<span class="lang-header">VĂN BẢN ĐÃ DỊCH</span>', unsafe_allow_html=True)
        res_txt = st.empty()
        res_txt.markdown('<div class="result-box">Kết quả dịch...</div>', unsafe_allow_html=True)

    if st.button(" BẮT ĐẦU DỊCH", key="btn_text"):
        if text_input.strip():
            full_prompt = f"{system_prompt}\n\n{text_input}"
            ans = translate_engine(full_prompt, temp_val, max_token_val)
            res_txt.markdown(f'<div class="result-box">{ans}</div>', unsafe_allow_html=True)

 
# TAB 2 – HÌNH ẢNH
 
with tab_image:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<span class="lang-header">TẢI ẢNH LÊN</span>', unsafe_allow_html=True)
        up_img = st.file_uploader("Upload Image", type=['png', 'jpg', 'jpeg'], label_visibility="collapsed")
        if up_img:
            st.image(Image.open(up_img), use_container_width=True)
    with col2:
        st.markdown('<span class="lang-header">KẾT QUẢ TRÍCH XUẤT & DỊCH</span>', unsafe_allow_html=True)
        res_img = st.empty()
        res_img.markdown('<div class="result-box">Đang đợi ảnh...</div>', unsafe_allow_html=True)

    if st.button(" QUÉT & DỊCH ẢNH", key="btn_img"):
        if up_img:
            content_payload = [system_prompt, Image.open(up_img)]
            ans = translate_engine(content_payload, temp_val, max_token_val)
            res_img.markdown(f'<div class="result-box">{ans}</div>', unsafe_allow_html=True)

 
# TAB 3 – TÀI LIỆU
 
with tab_doc:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<span class="lang-header">TẢI FILE PDF</span>', unsafe_allow_html=True)
        up_doc = st.file_uploader("Upload PDF", type=['pdf'], label_visibility="collapsed")
    with col2:
        st.markdown('<span class="lang-header">TRẠNG THÁI DỊCH</span>', unsafe_allow_html=True)
        res_doc = st.empty()
        res_doc.markdown('<div class="result-box">Đang đợi file PDF...</div>', unsafe_allow_html=True)

    if st.button(" DỊCH FILE PDF ", key="btn_doc"):
        if up_doc:
            reader = PdfReader(up_doc)
            start_page, trang_da_dich =  tai_tien_do()
            res_doc.markdown(f'<div class="result-box"> Tiếp tục từ trang {start_page + 1}</div>',unsafe_allow_html=True)

            try:
                for  index in range(start_page, len(reader.pages)):
                    res_doc.markdown(f'<div class="result-box">Đang dịch trang { index + 1} / {len(reader.pages)}</div>',unsafe_allow_html=True)
                    page_text = reader.pages[ index].extract_text()
                    if not page_text:
                        continue

                    translated = dich_trang_pdf(
                        page_text,
                        index + 1,
                        system_prompt,
                        temp_val,
                        max_token_val
                    )

                    trang_da_dich.append(f"\n--- Trang { index + 1} ---\n{translated}\n")
                    luu_tien_do( index + 1, trang_da_dich)
                    time.sleep(1)

                final_text = "".join(trang_da_dich)
                pdf_path = xuat_pdf_tieng_viet(final_text)

                with open(pdf_path, "rb") as f:
                    st.download_button(
                        "TẢI FILE PDF ĐÃ DỊCH",
                        f,
                        file_name="translated_vi.pdf",
                        mime="application/pdf"
                    )

                res_doc.markdown('<div class="result-box"> Dịch xong toàn bộ file PDF!</div>', unsafe_allow_html=True)

            except RuntimeError as e:
                res_doc.markdown(f'<div class="result-box">{str(e)}</div>', unsafe_allow_html=True)
