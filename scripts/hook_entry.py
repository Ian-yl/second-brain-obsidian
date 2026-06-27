"""本地 SessionEnd hook：对话结束后台从本次对话提炼新信息 → 写进本地 vault。

**纯本地、零外传**：后台起一个 `claude -p`/`codex exec` 子 agent，**带 `--strict-mcp-config`
（不加载任何 MCP，保持轻量、纯本地）**，让它读 transcript、按 vault-format.md
把关于用户的新信息写进 vault 的 markdown，不上传任何东西。

防递归：提炼子 agent 自身的 SessionEnd 也会触发本 hook，靠 env SBO_PROCESSING 护栏直接退出。
用法（由 install.py 注册）：python3 hook_entry.py --event end
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

RUNTIME = os.environ.get("SBO_RUNTIME_DIR") or os.path.expanduser("~/.second-brain-obsidian")
VAULT_FILE = os.path.join(RUNTIME, "vault_path")      # 建库/install 时写入的 vault 绝对路径
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FORMAT_REF = os.path.join(SKILL_DIR, "references", "vault-format.md")
IS_WINDOWS = os.name == "nt"


def _detach_kwargs():
    if IS_WINDOWS:
        return {"creationflags": 0x00000008 | 0x00000200}  # DETACHED_PROCESS|CREATE_NEW_PROCESS_GROUP
    return {"start_new_session": True}


def _engine():
    """提炼引擎：有 claude → claude -p（不加载 MCP/不开浏览器）；否则 codex exec。没有则 None。"""
    if shutil.which("claude"):
        return ["claude", "-p", "--strict-mcp-config", "--no-chrome", "--model", "haiku"]
    if shutil.which("codex"):
        return ["codex", "exec"]
    return None


def _prompt(transcript, vault):
    return (
        "你是「第二大脑」的本地维护器。任务：从一段对话里提炼关于【用户本人】有长期保留价值的新信息，"
        "写进本地 vault 的 markdown。**只写这个 vault 里的文件，绝不向任何地方上传。**\n\n"
        f"1) 读对话记录文件：{transcript}\n"
        "2) 提炼：用户的人格特征 / 决策 / 观点 / 方法 / 知识；**忽略**一次性闲聊、工具调用噪声、"
        "搭建本系统的元对话、任何密钥/token（绝不写进库）。没有可提炼的就什么都别写、直接结束。\n"
        f"3) 严格按格式规范写入 vault（规范见 {FORMAT_REF}）：vault 根目录 = {vault}\n"
        "   - 画像 → 用户画像.md 对应维度（去重；记一行变更日志）\n"
        "   - 知识 → Knowledge/<层>/<slug>.md（四层归类；同 slug 合并、不堆叠重复段落）\n"
        "   - 改完同步重写 CLAUDE.md + AGENTS.md（同内容）+ _索引.md\n"
    )


def main():
    # 防递归（最优先）：提炼子 agent 自身结束时不再触发提炼
    if os.environ.get("SBO_PROCESSING"):
        return
    ap = argparse.ArgumentParser()
    ap.add_argument("--event", default="end")
    args, _ = ap.parse_known_args()
    if args.event != "end":
        return  # 只在 SessionEnd 干活

    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except Exception:
        payload = {}
    transcript = payload.get("transcript_path") or payload.get("transcriptPath")
    if not transcript or not os.path.exists(transcript):
        return

    try:
        with open(VAULT_FILE, encoding="utf-8") as f:
            vault = f.read().strip()
    except Exception:
        return  # 还没建库/未记录 vault 路径 → 不做
    if not vault or not os.path.isdir(vault):
        return

    engine = _engine()
    if engine is None:
        return  # 没有 claude/codex 提炼引擎 → 跳过（其余功能不受影响）

    env = dict(os.environ, SBO_PROCESSING="1")  # 防递归护栏
    try:
        subprocess.Popen(
            engine + [_prompt(transcript, vault)],
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            env=env, **_detach_kwargs())
    except Exception:
        pass  # 任何异常静默退出，不打断用户


if __name__ == "__main__":
    main()
