"""语音密钥管理：写入 / 查看 ~/.second-brain-obsidian/secrets.env（chmod 600）。

可在安装时配置，也可随时单独唤醒（用户说「设置语音密钥」时）。密钥**只**存这里，
绝不进 vault / git / 日志。（模块名用 keys 而非 secrets，避免遮蔽 Python 标准库 secrets。）

CLI：
  keys.py status                                # 看哪些密钥已配（脱敏显示）
  keys.py set --azure-key K [--azure-region koreacentral]
              [--minimax-key K] [--minimax-host https://api.minimax.chat]
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import store  # noqa: E402

KNOWN = ["AZURE_SPEECH_KEY", "AZURE_SPEECH_REGION", "MINIMAX_API_KEY", "MINIMAX_API_HOST"]


def read_env():
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
    return env


def write_env(env):
    store.ensure_runtime_dir()
    lines = ["# second-brain-obsidian 语音密钥（chmod 600；勿提交 git / 勿进 vault）"]
    for k in KNOWN:
        if env.get(k):
            lines.append(f"{k}={env[k]}")
    store.atomic_write(store.SECRETS_PATH, "\n".join(lines) + "\n")
    try:
        os.chmod(store.SECRETS_PATH, 0o600)
    except OSError:
        pass


def _mask(v):
    if not v:
        return ""
    return (v[:4] + "…" + v[-4:]) if len(v) > 10 else "******"


def is_voice_configured():
    """实时语音采集需 Azure STT 的 key + region 都在（set_keys 设 key 时会自动补 region=koreacentral）。"""
    env = read_env()
    return bool(env.get("AZURE_SPEECH_KEY") and env.get("AZURE_SPEECH_REGION"))


def status():
    env = read_env()
    return {
        "path": store.SECRETS_PATH,
        "voice_ready": is_voice_configured(),
        "configured": {k: _mask(env.get(k, "")) for k in KNOWN if env.get(k)},
        "missing_required": [] if is_voice_configured() else ["AZURE_SPEECH_KEY"],
    }


def set_keys(azure_key=None, azure_region=None, minimax_key=None, minimax_host=None):
    env = read_env()
    if azure_key:
        env["AZURE_SPEECH_KEY"] = azure_key
        env.setdefault("AZURE_SPEECH_REGION", "koreacentral")
    if azure_region:
        env["AZURE_SPEECH_REGION"] = azure_region
    if minimax_key:
        env["MINIMAX_API_KEY"] = minimax_key
        env.setdefault("MINIMAX_API_HOST", "https://api.minimax.chat")
    if minimax_host:
        env["MINIMAX_API_HOST"] = minimax_host
    write_env(env)
    return status()


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    s = sub.add_parser("set")
    s.add_argument("--azure-key")
    s.add_argument("--azure-region")
    s.add_argument("--minimax-key")
    s.add_argument("--minimax-host")
    args = ap.parse_args()
    if args.cmd == "status":
        print(json.dumps(status(), ensure_ascii=False, indent=2))
    else:
        if not any([args.azure_key, args.azure_region, args.minimax_key, args.minimax_host]):
            print(json.dumps({"ok": False, "error": "no_keys",
                              "message": "至少给一个 --azure-key 等"}, ensure_ascii=False))
            sys.exit(2)
        res = set_keys(args.azure_key, args.azure_region, args.minimax_key, args.minimax_host)
        print(json.dumps({"ok": True, **res}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
