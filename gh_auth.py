"""GitHub 设备码授权（OAuth device flow），不依赖 gh CLI。

流程：
  1) 申请 device code，把 user_code 打印出来给用户
  2) 用户在 https://github.com/login/device 输入该码并授权
  3) 本脚本轮询拿到 access_token，写入 .gh_token（不打印）
用法：python gh_auth.py
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request

CLIENT_ID = "178c6fc778ccc68e1d6a"   # GitHub CLI 的公开 client_id
SCOPE = "repo read:user"
HERE = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = os.path.join(HERE, ".gh_token")


def post(url, data):
    body = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(url, data=body, headers={
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0",
    }, method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def main():
    d = post("https://github.com/login/device/code", {"client_id": CLIENT_ID, "scope": SCOPE})
    if "device_code" not in d:
        print("申请设备码失败:", d, flush=True)
        sys.exit(1)

    code = d["user_code"]
    uri = d.get("verification_uri", "https://github.com/login/device")
    interval = int(d.get("interval", 5))
    expires = int(d.get("expires_in", 900))

    print("=" * 60, flush=True)
    print(f"请在浏览器打开: {uri}", flush=True)
    print(f"输入验证码:    {code}", flush=True)
    print(f"（{expires // 60} 分钟内有效，我用你的 GitHub 账号授权，之后会自动写入 .gh_token）", flush=True)
    print("=" * 60, flush=True)

    deadline = time.time() + expires
    while time.time() < deadline:
        time.sleep(interval)
        try:
            r = post("https://github.com/login/oauth/access_token", {
                "client_id": CLIENT_ID,
                "device_code": d["device_code"],
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            })
        except Exception as e:
            print("  轮询异常，继续:", type(e).__name__, flush=True)
            continue
        err = r.get("error")
        if r.get("access_token"):
            tok = r["access_token"]
            with open(TOKEN_FILE, "w", encoding="utf-8") as f:
                f.write(tok.strip())
            try:
                os.chmod(TOKEN_FILE, 0o600)
            except Exception:
                pass
            print("AUTH OK  token 已保存到 .gh_token（未打印）", flush=True)
            return
        if err == "authorization_pending":
            continue
        if err == "slow_down":
            interval += 5
            continue
        if err in ("expired_token", "access_denied"):
            print("授权失败:", err, flush=True)
            sys.exit(2)
        print("  未知返回:", r, flush=True)
    print("超时，未完成授权", flush=True)
    sys.exit(3)


if __name__ == "__main__":
    main()
