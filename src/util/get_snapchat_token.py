# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : 88978827@qq.com
# app.py
from flask import Flask, request, redirect
import requests
import os

app = Flask(__name__)

# 配置：替换下面的值
CLIENT_ID = "46a131da-a98e-441b-bbdf-021868cd1dff"
CLIENT_SECRET = "aa7cd90798a55cade8b5"
REDIRECT_URI = "http://localhost:5050/callback"  # 必须与 Dashboard 一致
TOKEN_ENDPOINT = "https://accounts.snapchat.com/accounts/oauth2/token"


@app.route("/")
def index():
    # 指向授权 URL（可改 scope 或 state）
    auth_url = (
        "https://accounts.snapchat.com/login/oauth2/authorize"
        f"?response_type=code&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope=snapchat-marketing-api&state=xyz123"
    )
    return f'<a href="{auth_url}">Click to authorize Snapchat</a>'


@app.route("/callback")
def callback():
    code = request.args.get("code")
    state = request.args.get("state")
    if not code:
        return "No code in request", 400

    # 用 code 换 token
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
    }
    resp = requests.post(TOKEN_ENDPOINT, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
    return f"Token exchange response:<br/><pre>{resp.status_code} {resp.text}</pre>"


if __name__ == "__main__":
    app.run(port=5050, debug=True)
