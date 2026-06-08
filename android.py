import webview
from app import app

webview.create_window(
    "WarungPOS",
    app
)

webview.start()