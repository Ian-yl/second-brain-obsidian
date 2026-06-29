"""本地自动提炼 hook：把对话提炼进本地 vault（纯本地、零外传）。

两种模式（安装时由用户选，install.py 注册对应钩子）：
  --event end    SessionEnd：会话结束读【整段】对话、一次提炼（省）。
  --event stop   Stop（每条回复后）：【增量】只提炼上次之后的新内容（进度标记防重复）。

后台起 `claude -p`/`codex exec` 子 agent，**带 `--strict-mcp-config`（不加载任何 MCP，纯本地）**，
读对话、按 vault-format.md 把关于用户的信息写进 vault。不上传任何东西。
防递归：提炼子 agent 自身的钩子靠 env SBO_PROCESSING 护栏直接退出。
"""
import argparse
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

RUNTIME = os.environ.get("SBO_RUNTIME_DIR") or os.path.expanduser("~/.second-brain-obsidian")
VAULT_FILE = os.path.join(RUNTIME, "vault_path")          # 建库时记录的 vault 绝对路径
PROGRESS_FILE = os.path.join(RUNTIME, "stop-progress.json")  # Stop 增量进度：{transcript: 已处理行数}
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


def _vault():
    try:
        v = open(VAULT_FILE, encoding="utf-8").read().strip()
    except Exception:
        return None
    return v if v and os.path.isdir(v) else None


def _stop_chunk(transcript):
    """Stop 模式：把 transcript 里上次之后的新行写到临时文件，返回路径；无新内容返回 None。"""
    # 清掉超过 1 小时的旧分片，避免无限堆积
    for old in glob.glob(os.path.join(RUNTIME, "sbo-chunk-*.jsonl")):
        try:
            if time.time() - os.path.getmtime(old) > 3600:
                os.remove(old)
        except Exception:
            pass
    try:
        with open(transcript, encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
    except Exception:
        return None
    total = len(lines)
    prog = {}
    try:
        with open(PROGRESS_FILE, encoding="utf-8") as f:
            prog = json.load(f)
    except Exception:
        prog = {}
    done = int(prog.get(transcript, 0))
    if total <= done:
        return None  # 没有新内容
    fd, tmp = tempfile.mkstemp(prefix="sbo-chunk-", suffix=".jsonl", dir=RUNTIME)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.writelines(lines[done:])
    prog[transcript] = total
    try:
        with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
            json.dump(prog, f)
    except Exception:
        pass
    return tmp


def _prompt(source, vault, incremental):
    head = ("这是一段进行中对话的【最新片段】（更早的已提炼过，不要重复）"
            if incremental else "读这个对话记录文件")
    return (
        "你是「第二大脑」的本地维护器。任务：从对话里提炼关于【用户本人】有保留价值的新信息，"
        "写进本地 vault 的 markdown。**只写这个 vault 里的文件，绝不向任何地方上传。**\n\n"
        f"1) {head}：{source}\n"
        "2) 提炼：人格特征 / 决策 / 观点 / 方法 / 知识 / 在做的项目 / 自己搭建·运营的系统工具。"
        "**任何话题都不要跳过**（搭建本系统、闲聊、工具相关也照收）。"
        "唯一例外：明文密钥 / token / 密码不要写字面值，用「（已隐去）」代替。没有可提炼的才什么都别写。\n"
        f"3) 严格按格式规范写入 vault（规范见 {FORMAT_REF}）：vault 根目录 = {vault}\n"
        "   - 画像 → 用户画像.md 对应维度（去重；记一行变更日志）\n"
        "   - 知识 → Knowledge/<层>/<slug>.md（四层归类；同 slug 合并、不堆叠重复段落）\n"
        "   - 改完同步重写 CLAUDE.md + AGENTS.md（同内容）+ _索引.md\n"
    )


def main():
    if os.environ.get("SBO_PROCESSING"):   # 防递归：提炼子 agent 自身的钩子不再触发
        return
    ap = argparse.ArgumentParser()
    ap.add_argument("--event", default="end")   # end（SessionEnd 整段）| stop（每条回复增量）
    args, _ = ap.parse_known_args()
    if args.event not in ("end", "stop"):
        return

    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except Exception:
        payload = {}
    transcript = payload.get("transcript_path") or payload.get("transcriptPath")
    if not transcript or not os.path.exists(transcript):
        return

    vault = _vault()
    if not vault:
        return  # 还没建库 / 没记录 vault 路径

    incremental = args.event == "stop"
    source = _stop_chunk(transcript) if incremental else transcript
    if not source:
        return  # stop 模式：无新内容

    engine = _engine()
    if engine is None:
        return  # 没有 claude/codex 提炼引擎

    env = dict(os.environ, SBO_PROCESSING="1")   # 防递归护栏
    try:
        subprocess.Popen(
            engine + [_prompt(source, vault, incremental)],
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            env=env, **_detach_kwargs())
    except Exception:
        pass


if __name__ == "__main__":
    main()
