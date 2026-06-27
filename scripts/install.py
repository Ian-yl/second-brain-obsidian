"""注册【本地】SessionEnd hook：对话结束自动提炼写 vault（纯本地、零外传）。

vault 路径在【初始化建库】时已记录到 ~/.second-brain-obsidian/vault_path，
本脚本**固定读它、不接受路径参数**（要换库就重新初始化）。自愈：先清掉旧的 SessionStart/SessionEnd 条目再写回。

用法：
  python3 install.py            # 注册 SessionEnd hook（vault 路径取自初始化记录）
  python3 install.py --remove   # 注销
"""
import argparse
import json
import os
import sys

RUNTIME = os.environ.get("SBO_RUNTIME_DIR") or os.path.expanduser("~/.second-brain-obsidian")
VAULT_FILE = os.path.join(RUNTIME, "vault_path")
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
HOOK = os.path.join(SCRIPTS_DIR, "hook_entry.py")

# 各 agent 的 hook 配置文件
HOOK_FILES = {
    "claude": os.path.expanduser("~/.claude/settings.json"),
    "codex": os.path.expanduser("~/.codex/hooks.json"),
}
OUR_EVENTS = ("SessionStart", "SessionEnd")  # 清理时两者都扫（含历史遗留），自愈重写


def _hook_command():
    py = sys.executable or "python3"   # 跨平台：当前解释器绝对路径（Win 上常没有 python3）
    return f'"{py}" "{HOOK}" --event end'


def _is_ours(group):
    return isinstance(group, dict) and any(
        isinstance(h, dict) and "hook_entry.py" in h.get("command", "")
        for h in group.get("hooks", []))


def _register(path, remove=False):
    data = {}
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}
    hooks = data.setdefault("hooks", {})
    # 自愈：先移除我们在 SessionStart/SessionEnd 名下注册过的条目（含历史遗留），不动别人的 hook
    for event in OUR_EVENTS:
        if event in hooks:
            hooks[event] = [g for g in hooks[event] if not _is_ours(g)]
            if not hooks[event]:
                del hooks[event]
    if not remove:
        hooks.setdefault("SessionEnd", []).append(
            {"hooks": [{"type": "command", "command": _hook_command(), "timeout": 30}]})
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return "removed" if remove else "registered"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--remove", action="store_true", help="注销本地 hook")
    args = ap.parse_args()
    os.makedirs(RUNTIME, exist_ok=True)

    if args.remove:
        res = {a: _register(p, remove=True) for a, p in HOOK_FILES.items()}
        print(json.dumps({"ok": True, "removed": res}, ensure_ascii=False))
        return

    # vault 路径在【初始化建库】时已记录；这里固定读它，不接受路径参数
    try:
        with open(VAULT_FILE, encoding="utf-8") as f:
            vault = f.read().strip()
    except Exception:
        vault = ""
    if not vault or not os.path.isdir(vault):
        print(json.dumps({"ok": False, "error": "未找到 vault：请先初始化建库（建库会把 vault 路径记进 ~/.second-brain-obsidian/vault_path）"}, ensure_ascii=False))
        sys.exit(2)

    res = {a: _register(p) for a, p in HOOK_FILES.items()}
    print(json.dumps({
        "ok": True, "vault": vault, "hooks": res,
        "note": "本地 SessionEnd hook 已注册：每次对话结束后台提炼写进 vault（路径取自初始化记录，纯本地、不外传）。注销用 --remove。",
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
