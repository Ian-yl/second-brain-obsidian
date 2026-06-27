#!/usr/bin/env python3
"""实时语音问答本地服务。

浏览器用微软 Azure Speech SDK 做**实时** STT；密钥留服务端，只把 10 分钟短期
token 下发给浏览器。问题用浏览器 TTS 朗读，回答经 Azure STT 实时转写后回收。

用法：
  python3 scripts/voice/bridge.py --questions /tmp/q.json --out /tmp/answers.json [--port 8765]
其中 q.json 形如 ["问题1", "问题2", ...]。结束后 answers.json 形如
  [{"q": "问题1", "a": "用户语音转写"}, ...]

依赖 secrets.env（或环境变量）：AZURE_SPEECH_KEY、AZURE_SPEECH_REGION。
"""
import argparse
import http.server
import json
import os
import subprocess
import sys
import threading
import urllib.request
import webbrowser

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import store  # noqa: E402

WEB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")


def load_secrets():
    env = {}
    if os.path.exists(store.SECRETS_PATH):
        try:
            with open(store.SECRETS_PATH, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, _, v = line.partition("=")
                        env[k.strip()] = v.strip().strip('"').strip("'")
        except Exception:
            pass
    for k in ("AZURE_SPEECH_KEY", "AZURE_SPEECH_REGION", "MINIMAX_API_KEY"):
        env.setdefault(k, os.environ.get(k, ""))
    env.setdefault("AZURE_SPEECH_REGION", "koreacentral")
    return env


def issue_azure_token(secrets):
    region = secrets.get("AZURE_SPEECH_REGION") or "koreacentral"
    key = secrets.get("AZURE_SPEECH_KEY") or ""
    if not key:
        raise RuntimeError("secrets.env 缺少 AZURE_SPEECH_KEY")
    url = f"https://{region}.api.cognitive.microsoft.com/sts/v1.0/issueToken"
    req = urllib.request.Request(
        url, data=b"",
        headers={"Ocp-Apim-Subscription-Key": key, "Content-Length": "0"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return r.read().decode()


def minimax_tts(text, secrets):
    """MiniMax 文字转语音 → mp3 bytes（只用 API key，无需 GroupId，已实测）。"""
    key = secrets.get("MINIMAX_API_KEY") or ""
    if not key:
        raise RuntimeError("no minimax key")
    host = (secrets.get("MINIMAX_API_HOST") or "https://api.minimax.chat").rstrip("/")
    voice_id = secrets.get("MINIMAX_VOICE_ID") or "male-qn-qingse"
    body = json.dumps({
        "model": "speech-01-turbo", "text": text, "stream": False,
        "voice_setting": {"voice_id": voice_id, "speed": 1.0, "vol": 1.0, "pitch": 0},
        "audio_setting": {"sample_rate": 32000, "bitrate": 128000, "format": "mp3", "channel": 1},
    }).encode()
    req = urllib.request.Request(
        host + "/v1/t2a_v2", data=body,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.load(r)
    audio_hex = (d.get("data") or {}).get("audio") or ""
    if not audio_hex:
        raise RuntimeError("minimax 返回空音频: " + json.dumps(d.get("base_resp", {}), ensure_ascii=False))
    return bytes.fromhex(audio_hex)


class State:
    def __init__(self, questions, out_path):
        self.questions = questions
        self.out_path = out_path
        self.answers = []
        self.reason = "in_progress"   # completed / hangup / error / closed / in_progress
        self.done = threading.Event()
        self._close_timer = None      # 关页延时退出定时器（刷新会取消它）


def make_handler(state, secrets):
    class Handler(http.server.BaseHTTPRequestHandler):
        def _send(self, code, body, ctype="application/json"):
            data = body.encode("utf-8") if isinstance(body, str) else body
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, *a):
            pass  # 静音

        def do_GET(self):
            if self.path == "/" or self.path.startswith("/index"):
                if state._close_timer:      # 又加载了页面 = 刷新，不是关闭 → 取消退出
                    state._close_timer.cancel()
                    state._close_timer = None
                state.answers.clear()       # 每次打开/刷新页面 = 一次新通话，重置
                state.reason = "in_progress"
                with open(os.path.join(WEB_DIR, "index.html"), "rb") as f:
                    return self._send(200, f.read(), "text/html; charset=utf-8")
            if self.path == "/questions":
                return self._send(200, json.dumps(state.questions, ensure_ascii=False))
            if self.path == "/token":
                try:
                    tok = issue_azure_token(secrets)
                    region = secrets.get("AZURE_SPEECH_REGION") or "koreacentral"
                    return self._send(200, json.dumps({"token": tok, "region": region}))
                except Exception as e:
                    return self._send(500, json.dumps({"error": str(e)}))
            return self._send(404, json.dumps({"error": "not found"}))

        def do_POST(self):
            n = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(n) if n else b"{}"
            try:
                payload = json.loads(raw or b"{}")
            except Exception:
                payload = {}
            if self.path == "/tts":
                try:
                    audio = minimax_tts(payload.get("text", ""), secrets)
                    return self._send(200, audio, "audio/mpeg")
                except Exception as e:
                    return self._send(500, json.dumps({"error": str(e)}))
            if self.path == "/answer":
                state.answers.append({"q": payload.get("q", ""), "a": payload.get("a", "")})
                _write_out(state)
                return self._send(200, json.dumps({"ok": True, "count": len(state.answers)}))
            if self.path == "/done":
                state.reason = payload.get("reason") or "completed"
                _write_out(state)
                self._send(200, json.dumps({"ok": True, "reason": state.reason}))
                if state.reason in ("completed", "hangup"):
                    state.done.set()        # 答完 / 主动挂断 → 立即停
                elif state.reason == "closed":
                    # 可能是刷新（会很快再 GET /）也可能是关闭：延时 3s 判定，刷新会取消
                    if state._close_timer:
                        state._close_timer.cancel()
                    state._close_timer = threading.Timer(3.0, state.done.set)
                    state._close_timer.daemon = True
                    state._close_timer.start()
                # error → 保持运行，方便重试
                return
            return self._send(404, json.dumps({"error": "not found"}))

    return Handler


def _write_out(state):
    try:
        store.atomic_write(state.out_path, json.dumps(
            {"reason": state.reason, "count": len(state.answers), "answers": state.answers},
            ensure_ascii=False, indent=2))
    except Exception:
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--questions", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--no-open", action="store_true")
    ap.add_argument("--background", action="store_true",
                    help="后台启服务、立即返回 URL（不阻塞 agent；推荐）")
    args = ap.parse_args()

    with open(args.questions, encoding="utf-8") as f:
        questions = json.load(f)
    secrets = load_secrets()
    if not secrets.get("AZURE_SPEECH_KEY"):
        print(json.dumps({"ok": False, "error": "missing_azure_key",
                          "message": f"请在 {store.SECRETS_PATH} 填 AZURE_SPEECH_KEY"},
                         ensure_ascii=False))
        sys.exit(2)

    url = f"http://127.0.0.1:{args.port}/"

    # 后台模式：派生一个 detached 子进程跑服务，父进程开浏览器 + 打印 URL 立即返回
    if args.background:
        child = [sys.executable, os.path.abspath(__file__), "--questions", args.questions,
                 "--out", args.out, "--port", str(args.port), "--no-open"]
        subprocess.Popen(child, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL, **store.detach_kwargs())
        if not args.no_open:
            try:
                webbrowser.open(url)
            except Exception:
                pass
        print(json.dumps({"ok": True, "background": True, "url": url, "out": args.out,
                          "message": "语音服务已后台启动。让用户在浏览器打开 url 做语音问答；"
                                     "答完后读 out 文件、把答案提炼写进画像（见 vault-format.md）"},
                         ensure_ascii=False))
        return

    # 前台模式：serve_forever 直到浏览器 /done（会阻塞，调试用）
    state = State(questions, args.out)
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(state, secrets))
    print(json.dumps({"ok": True, "url": url, "questions": len(questions),
                      "out": args.out, "message": "在浏览器打开 URL 进行实时语音问答；完成后本服务自动退出"},
                     ensure_ascii=False))
    if not args.no_open:
        try:
            webbrowser.open(url)
        except Exception:
            pass
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    state.done.wait()  # 等浏览器 /done
    httpd.shutdown()
    print(json.dumps({"ok": True, "answers": len(state.answers), "out": args.out},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
