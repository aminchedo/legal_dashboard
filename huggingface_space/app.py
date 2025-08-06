"""
Gradio Interface for Legal Dashboard - Hugging Face Spaces
==========================================================
This provides a web interface for the Legal Dashboard using Gradio,
optimized for deployment on Hugging Face Spaces.
"""

import os
import sys
import asyncio
import threading
import time
import gradio as gr
import requests
from typing import Optional, Dict, Any

# Add app directory to Python path
sys.path.insert(0, '/app')
sys.path.insert(0, '.')

# Set environment variables for the app
os.environ.setdefault('DATABASE_DIR', '/tmp/legal_dashboard')
os.environ.setdefault('PYTHONPATH', '/app')
os.environ.setdefault('LOG_LEVEL', 'INFO')

# Global variables
fastapi_server = None
server_port = 7860

def start_fastapi_server():
    """Start FastAPI server in a separate thread"""
    global fastapi_server, server_port
    
    try:
        import uvicorn
        from app.main import app
        
        print(f"🚀 Starting FastAPI server on port {server_port}...")
        
        # Run FastAPI server
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=server_port,
            log_level="info",
            access_log=False
        )
    except Exception as e:
        print(f"❌ Failed to start FastAPI server: {e}")
        return None

def wait_for_server(timeout=30):
    """Wait for FastAPI server to be ready"""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"http://127.0.0.1:{server_port}/health", timeout=2)
            if response.status_code == 200:
                print("✅ FastAPI server is ready!")
                return True
        except:
            pass
        time.sleep(1)
    
    print("❌ FastAPI server failed to start within timeout")
    return False

def make_api_request(endpoint: str, method: str = "GET", data: Dict = None, token: str = None) -> Dict:
    """Make request to FastAPI backend"""
    url = f"http://127.0.0.1:{server_port}{endpoint}"
    headers = {}
    
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    if method == "POST" and data:
        headers["Content-Type"] = "application/json"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=10)
        else:
            return {"error": f"Unsupported method: {method}"}
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"HTTP {response.status_code}: {response.text}"}
    
    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}

# Authentication state
auth_state = {"token": None, "user": None}

def login_user(username: str, password: str) -> tuple:
    """Login user and return status"""
    if not username or not password:
        return False, "نام کاربری و رمز عبور الزامی است", "", ""
    
    data = {"username": username, "password": password}
    result = make_api_request("/api/auth/login", "POST", data)
    
    if "error" in result:
        return False, f"خطا در ورود: {result['error']}", "", ""
    
    if "access_token" in result:
        auth_state["token"] = result["access_token"]
        
        # Get user info
        user_info = make_api_request("/api/auth/me", "GET", token=auth_state["token"])
        if "error" not in user_info:
            auth_state["user"] = user_info
            return True, f"خوش آمدید {user_info.get('username', 'کاربر')}!", "", ""
    
    return False, "ورود ناموفق", "", ""

def register_user(username: str, email: str, password: str) -> tuple:
    """Register new user"""
    if not all([username, email, password]):
        return False, "تمام فیلدها الزامی است", "", "", ""
    
    data = {
        "username": username,
        "email": email,
        "password": password,
        "role": "user"
    }
    
    result = make_api_request("/api/auth/register", "POST", data)
    
    if "error" in result:
        return False, f"خطا در ثبت نام: {result['error']}", "", "", ""
    
    return True, "ثبت نام موفقیت آمیز بود. اکنون می‌توانید وارد شوید.", "", "", ""

def logout_user():
    """Logout current user"""
    if auth_state["token"]:
        make_api_request("/api/auth/logout", "POST", token=auth_state["token"])
    
    auth_state["token"] = None
    auth_state["user"] = None
    return False, "خروج موفقیت آمیز", "", ""

def get_server_status():
    """Get server status"""
    try:
        response = make_api_request("/health")
        if "error" not in response:
            return f"✅ Server Status: {response.get('status', 'Unknown')}"
        else:
            return f"❌ Server Error: {response['error']}"
    except:
        return "❌ Server not responding"

def process_document(file, document_type: str = "قرارداد"):
    """Process uploaded document"""
    if not file:
        return "لطفاً فایلی را انتخاب کنید"
    
    if not auth_state["token"]:
        return "لطفاً ابتدا وارد شوید"
    
    # This would integrate with your document processing API
    return f"فایل '{file.name}' از نوع '{document_type}' در حال پردازش است..."

# Start FastAPI server in background
def start_background_server():
    """Start FastAPI server in background thread"""
    server_thread = threading.Thread(target=start_fastapi_server, daemon=True)
    server_thread.start()
    
    # Wait for server to be ready
    if wait_for_server():
        print("🎉 System ready!")
    else:
        print("⚠️ System may not be fully functional")

# Start the background server
start_background_server()

# Create Gradio interface
with gr.Blocks(
    title="Legal Dashboard - داشبورد حقوقی",
    theme=gr.themes.Soft(),
    css="""
    .container { max-width: 1200px; margin: auto; }
    .login-box { background: #f8f9fa; padding: 20px; border-radius: 10px; }
    .status-box { background: #e7f3ff; padding: 10px; border-radius: 5px; margin: 10px 0; }
    """,
    rtl=True
) as app:
    
    gr.Markdown("""
    # 📊 داشبورد حقوقی
    ### سیستم مدیریت و تحلیل اسناد حقوقی
    
    این سیستم امکان آپلود، تحلیل و مدیریت اسناد حقوقی را فراهم می‌کند.
    """)
    
    # Authentication section
    with gr.Tab("🔐 احراز هویت"):
        with gr.Row():
            with gr.Column():
                gr.Markdown("### ورود به سیستم")
                login_username = gr.Textbox(label="نام کاربری", placeholder="admin")
                login_password = gr.Textbox(label="رمز عبور", type="password", placeholder="admin123")
                login_btn = gr.Button("ورود", variant="primary")
                login_status = gr.Textbox(label="وضعیت", interactive=False)
            
            with gr.Column():
                gr.Markdown("### ثبت نام")
                reg_username = gr.Textbox(label="نام کاربری")
                reg_email = gr.Textbox(label="ایمیل")
                reg_password = gr.Textbox(label="رمز عبور", type="password")
                register_btn = gr.Button("ثبت نام", variant="secondary")
                reg_status = gr.Textbox(label="وضعیت", interactive=False)
        
        with gr.Row():
            logout_btn = gr.Button("خروج", variant="stop")
            server_status = gr.Textbox(label="وضعیت سرور", value=get_server_status, every=30)
    
    # Document processing section
    with gr.Tab("📄 پردازش اسناد"):
        gr.Markdown("### آپلود و تحلیل اسناد")
        
        with gr.Row():
            with gr.Column():
                file_input = gr.File(
                    label="انتخاب فایل",
                    file_types=[".pdf", ".docx", ".doc", ".txt"],
                    type="filepath"
                )
                doc_type = gr.Dropdown(
                    label="نوع سند",
                    choices=["قرارداد", "دادخواست", "رأی دادگاه", "سند اداری", "سایر"],
                    value="قرارداد"
                )
                process_btn = gr.Button("پردازش سند", variant="primary")
            
            with gr.Column():
                process_result = gr.Textbox(
                    label="نتیجه پردازش",
                    lines=10,
                    interactive=False
                )
    
    # System information
    with gr.Tab("ℹ️ اطلاعات سیستم"):
        gr.Markdown("""
        ### راهنمای استفاده
        
        **احراز هویت:**
        - کاربر پیش‌فرض: `admin` / `admin123`
        - برای دسترسی کامل ابتدا وارد شوید
        
        **پردازش اسناد:**
        - فرمت‌های پشتیبانی شده: PDF, DOCX, DOC, TXT
        - حداکثر حجم فایل: 50MB
        
        **ویژگی‌ها:**
        - تحلیل متن با هوش مصنوعی
        - استخراج اطلاعات کلیدی
        - تشخیص نوع سند
        - آرشیو و مدیریت اسناد
        """)
        
        api_status = gr.JSON(
            label="وضعیت API",
            value=lambda: make_api_request("/health")
        )

    # Event handlers
    login_btn.click(
        fn=login_user,
        inputs=[login_username, login_password],
        outputs=[gr.State(), login_status, login_username, login_password]
    )
    
    register_btn.click(
        fn=register_user,
        inputs=[reg_username, reg_email, reg_password],
        outputs=[gr.State(), reg_status, reg_username, reg_email, reg_password]
    )
    
    logout_btn.click(
        fn=logout_user,
        outputs=[gr.State(), login_status, login_username, login_password]
    )
    
    process_btn.click(
        fn=process_document,
        inputs=[file_input, doc_type],
        outputs=[process_result]
    )

# Launch configuration for Hugging Face Spaces
if __name__ == "__main__":
    # Check if running in HF Spaces
    if os.getenv("SPACE_ID"):
        print("🤗 Running in Hugging Face Spaces")
        app.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,
            show_error=True,
            debug=False
        )
    else:
        print("🖥️ Running locally")
        app.launch(
            server_name="127.0.0.1",
            server_port=7860,
            share=True,
            show_error=True,
            debug=True
        )