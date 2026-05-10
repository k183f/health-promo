# -*- coding: utf-8 -*-
"""
健康证管理系统 - 桌面版
启动后显示前台页面，可通过菜单切换到后台管理
"""

import webview
import os
import sys
import json
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.parse

# ============ 配置 ============
PORT = 18234
WINDOW_TITLE = "健康证管理系统"
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
# ==============================

# 找到HTML文件目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# 优先使用本目录下的文件，其次使用TEMP目录
DEPLOY_DIR = os.path.join(os.environ.get('TEMP', '/tmp'), 'health-cert-deploy')
if not os.path.exists(os.path.join(SCRIPT_DIR, 'index.html')) and os.path.exists(DEPLOY_DIR):
    HTML_DIR = DEPLOY_DIR
else:
    HTML_DIR = SCRIPT_DIR


class HealthCertHandler(SimpleHTTPRequestHandler):
    """自定义HTTP处理器，支持CORS和JSON API"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=HTML_DIR, **kwargs)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-cache')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        # 静默日志
        pass


def start_server():
    """在后台线程启动HTTP服务器"""
    server = HTTPServer(('127.0.0.1', PORT), HealthCertHandler)
    server.serve_forever()


def get_api(js_api):
    """获取JS API类"""
    class Api:
        def __init__(self):
            pass

        def switch_to_admin(self):
            """切换到后台管理页面"""
            window = webview.windows[0]
            window.load_url(f'http://127.0.0.1:{PORT}/admin.html')
            window.set_title(f"{WINDOW_TITLE} - 后台管理")

        def switch_to_front(self):
            """切换到前台用户页面"""
            window = webview.windows[0]
            window.load_url(f'http://127.0.0.1:{PORT}/index.html')
            window.set_title(f"{WINDOW_TITLE} - 前台")

        def show_about(self):
            """显示关于信息"""
            window = webview.windows[0]
            window.create_window(
                f"{WINDOW_TITLE} - 关于",
                html="""
                <html>
                <head><style>
                    body { font-family: 'Microsoft YaHei', sans-serif; padding: 40px; text-align: center; background: #f5f5f5; }
                    h1 { color: #2c3e50; }
                    p { color: #666; font-size: 16px; }
                </style></head>
                <body>
                    <h1>🏥 健康证管理系统</h1>
                    <p>版本 1.0.0</p>
                    <p>桌面版 - Python + pywebview</p>
                    <br>
                    <button onclick="window.close()" style="padding: 8px 24px; font-size: 16px; cursor: pointer;">关闭</button>
                </body>
                </html>
                """,
                width=400, height=300, resizable=False
            )

        def get_version(self):
            return "1.0.0"

    return Api()


if __name__ == '__main__':
    print(f"正在启动 {WINDOW_TITLE}...")
    print(f"HTML 目录: {HTML_DIR}")

    # 验证HTML文件存在
    index_path = os.path.join(HTML_DIR, 'index.html')
    admin_path = os.path.join(HTML_DIR, 'admin.html')
    if not os.path.exists(index_path):
        print(f"错误: 找不到 index.html，请将HTML文件放到 {HTML_DIR}")
        sys.exit(1)

    # 后台启动HTTP服务
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    # 创建API
    api = get_api(None)

    # 创建窗口
    window = webview.create_window(
        title=WINDOW_TITLE,
        url=f'http://127.0.0.1:{PORT}/index.html',
        js_api=api,
        width=WINDOW_WIDTH,
        height=WINDOW_HEIGHT,
        min_size=(800, 600),
        text_select=True
    )

    # 启动应用
    print("启动成功！关闭窗口即可退出。")
    webview.start(debug=False)
