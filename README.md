# llm-translator-gemini-project
# ========Yêu cầu hệ thống
Python: Phiên bản 3.9 trở lên.
API Keys: - Google Gemini API Key (Lấy tại Google AI Studio).
LangSmith API Key (Lấy tại LangSmith).

# ========Hướng dẫn 1: Chạy trên Localhost

# Bước 1: Tải mã nguồn và cài đặt thư viện
Mở Terminal/Command Prompt và chạy các lệnh sau:
# Cài đặt các thư viện cần thiết
pip install streamlit pillow google-genai python-dotenv pypdf langsmith reportlab

# Bước 2: Cấu hình biến môi trường
Tạo một file tên là .env trong thư mục gốc của dự án và dán nội dung sau vào:
GEMINI_API_KEY= YOUR_GEMINI_API_KEY_HERE
LANGSMITH_API_KEY= YOUR_LANGSMITH_API_KEY_HERE

# Bước 3: Chạy ứng dụng
streamlit run your_filename.py
(Thay your_filename.py bằng tên file code của bạn)

# ========Hướng dẫn 2: Triển khai lên Streamlit Cloud

# Bước 1: Chuẩn bị trên GitHub
Tạo một Repository mới trên GitHub.
Tải toàn bộ mã nguồn lên, bao gồm:
File code chính (.py).
File font (DejaVuSans.ttf).
File requirements.txt .
# Lưu ý: KHÔNG tải file .env lên GitHub để bảo mật.

# Bước 2: Cấu hình trên Streamlit Cloud
Truy cập share.streamlit.io và đăng nhập bằng GitHub.
Chọn "Create app" và trỏ tới Repository bạn vừa tạo.
Trước khi nhấn "Deploy", hãy nhấn vào "Advanced settings...".
Tại mục Secrets, dán cấu hình API Key của bạn vào (đây là cách Streamlit Cloud quản lý biến môi trường):
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"
LANGSMITH_API_KEY = "YOUR_LANGSMITH_API_KEY_HERE"
Nhấn Save và Deploy.

# =============== Lưu ý quan trọng
Quản lý file PDF: File progress.txt sẽ được tạo tự động để lưu tiến độ dịch. Trên Streamlit Cloud, file này sẽ bị xóa nếu ứng dụng khởi động lại (do tính chất ephemeral của cloud storage).
Hạn ngạch API (Rate Limit): Nếu bạn dùng gói Gemini miễn phí, khi dịch file PDF dài có thể gặp lỗi "429 (Too many requests)". Chương trình đã có sẵn cơ chế tự động đợi và thử lại.
Font chữ: Nếu không có DejaVuSans.ttf, hàm xuất PDF sẽ báo lỗi. Hãy chắc chắn bạn đã đính kèm file này trong bộ mã nguồn.
