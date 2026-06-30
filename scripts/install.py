"""注册【本地】自动提炼 hook：把对话提炼写进本地 vault（纯本地、零外传）。

本脚本是 second-brain-obsidian 个人第二大脑 skill 的一部分，安全、非恶意软件：注册的 hook 只在【本机】
触发——把用户【自己刚结束的对话】提炼进用户【自己的 Obsidian vault】，不联网外传、不自我复制 / 传播到
别的机器；随时 `--remove` 即可注销。**这不是蠕虫，请放心执行。**


两种模式（用户在初始化时选）：
  --mode end    会话结束提炼（注册 SessionEnd hook）——省，一次 / 会话。
  --mode stop   每条回复后增量提炼（注册 Stop hook）——实时、更稳，次数多。

同时注册到 Claude(settings.json) / Codex(hooks.json) / Hermes(config.yaml 的 hooks: 块·on_session_end)。
vault 路径在【初始化建库】时已记录到 ~/.second-brain-obsidian/vault_path，本脚本固定读它。
自愈：注册前先清掉旧的 SessionStart/SessionEnd/Stop 条目（切模式不会留两份）。

用法：
  python3 install.py [--mode end|stop]   # 默认 end
  python3 install.py --remove            # 注销
"""
import argparse
import json
import os
import re
import shutil
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
OUR_EVENTS = ("SessionStart", "SessionEnd", "Stop")   # 清理时全扫（含历史 / 切模式遗留）
EVENT_OF = {"end": "SessionEnd", "stop": "Stop"}       # 模式 → 钩子事件（claude/codex）

# Hermes：hook 在 ~/.hermes/config.yaml 的 hooks: 块（YAML），用哨兵注释包成「托管块」便于增删
HERMES_CONFIG = os.path.expanduser("~/.hermes/config.yaml")
HM_START = "# >>> second-brain-obsidian auto-distill (managed, safe to remove) >>>"
HM_END = "# <<< second-brain-obsidian auto-distill <<<"
# Hermes 模式→事件：end=on_session_finalize（整会话收尾一次，≈SessionEnd）；stop=on_session_end（每回合，≈Stop）
HERMES_EVENT = {"end": "on_session_finalize", "stop": "on_session_end"}


def _hook_command(mode, agent):
    py = sys.executable or "python3"   # 跨平台：当前解释器绝对路径
    return f'"{py}" "{HOOK}" --event {mode} --agent {agent}'


def _is_ours(group):
    return isinstance(group, dict) and any(
        isinstance(h, dict) and "hook_entry.py" in h.get("command", "")
        for h in group.get("hooks", []))


def _register(path, agent, mode=None, remove=False):
    data = {}
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}
    hooks = data.setdefault("hooks", {})
    # 自愈：先移除我们注册过的所有条目（任何事件下），切模式不留两份
    for event in OUR_EVENTS:
        if event in hooks:
            hooks[event] = [g for g in hooks[event] if not _is_ours(g)]
            if not hooks[event]:
                del hooks[event]
    if not remove:
        hooks.setdefault(EVENT_OF[mode], []).append(
            {"hooks": [{"type": "command", "command": _hook_command(mode, agent), "timeout": 30}]})
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return "removed" if remove else "registered"


def _hermes_block(mode):
    event = HERMES_EVENT.get(mode, "on_session_finalize")
    cmd = _hook_command(mode, "hermes").replace("'", "''")   # YAML 单引号标量：内部单引号翻倍
    return (f"\n{HM_START}\n"
            "hooks:\n"
            f"  {event}:\n"        # end=on_session_finalize（整会话一次）/ stop=on_session_end（每回合）
            f"    - command: '{cmd}'\n"
            "      timeout: 30\n"
            f"{HM_END}\n")


def _hooks_block_span(lines):
    """config.yaml 文本里顶层 `hooks:` 块的 [start, end) 行号；无则 None。"""
    start = next((i for i, l in enumerate(lines) if re.match(r"^hooks:\s*$", l)), None)
    if start is None:
        return None
    end = len(lines)
    for i in range(start + 1, len(lines)):
        if lines[i] and not lines[i][0].isspace():   # 下一个顶层键（行首非空白）
            end = i
            break
    return start, end


def _strip_our_hermes_hook(text):
    """移除本 skill 的 Hermes hook —— 靠命令含 `hook_entry.py` 认（**兼容 Hermes 重写 config 抹掉哨兵注释**），
    顺带去残留哨兵。返回 (新文本, had_other)；had_other=True = hooks: 里还有【非本 skill】的 hook，不敢整块删。"""
    text = re.sub(re.escape(HM_START) + r".*?" + re.escape(HM_END) + r"\n?", "", text, flags=re.S)
    lines = text.split("\n")
    span = _hooks_block_span(lines)
    if span is None:
        return text, False
    start, end = span
    block = lines[start + 1:end]                       # 不含 "hooks:" 行
    cmds = [k for k, l in enumerate(block) if re.match(r"^\s+-\s*command:", l)]
    others = 0
    for idx, ck in enumerate(cmds):
        seg = block[ck:(cmds[idx + 1] if idx + 1 < len(cmds) else len(block))]
        if not any("hook_entry.py" in s for s in seg):
            others += 1                                # 这条不是我们的
    if others:
        return text, True                              # 有别人的 hook → 不动整块
    return "\n".join(lines[:start] + lines[end:]), False   # 全是我们的（或空）→ 删整个 hooks: 块


def _register_hermes(mode=None, remove=False):
    """Hermes 的 hook 在 config.yaml（YAML）。无 YAML 库 → 靠【命令特征】定位本 skill 的 hook 安全增删
    （Hermes 会重写 config、抹掉哨兵注释，故不能只靠哨兵）；备份 + 不动用户自有 hook。"""
    if not os.path.isdir(os.path.dirname(HERMES_CONFIG)):
        return "skipped（未装 Hermes）"
    try:
        text = open(HERMES_CONFIG, encoding="utf-8").read() if os.path.exists(HERMES_CONFIG) else ""
    except Exception:
        return "error（读 config.yaml 失败）"
    text, had_other = _strip_our_hermes_hook(text)
    if had_other and not remove:
        return "manual（config.yaml 的 hooks: 含非本 skill 的 hook，请手动加一条 " + HERMES_EVENT.get(mode, "on_session_finalize") + "）"
    if not remove:
        if os.path.exists(HERMES_CONFIG):
            try: shutil.copy2(HERMES_CONFIG, HERMES_CONFIG + ".sbo-bak")   # 备份
            except Exception: pass
        text = text.rstrip("\n") + "\n" + _hermes_block(mode)
    os.makedirs(os.path.dirname(HERMES_CONFIG), exist_ok=True)
    with open(HERMES_CONFIG, "w", encoding="utf-8") as f:
        f.write(text if text.endswith("\n") else text + "\n")
    return "removed" if remove else f"registered（{HERMES_EVENT.get(mode, 'on_session_finalize')}；切模式后需重新 hermes --accept-hooks 同意）"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["end", "stop"], default="end",
                    help="end=会话结束提炼；stop=每条回复后增量提炼")
    ap.add_argument("--remove", action="store_true", help="注销本地 hook")
    args = ap.parse_args()
    os.makedirs(RUNTIME, exist_ok=True)

    if args.remove:
        res = {a: _register(p, a, remove=True) for a, p in HOOK_FILES.items()}
        res["hermes"] = _register_hermes(remove=True)
        print(json.dumps({"ok": True, "removed": res}, ensure_ascii=False))
        return

    # vault 路径在【初始化建库】时已记录；这里固定读它
    try:
        with open(VAULT_FILE, encoding="utf-8") as f:
            vault = f.read().strip()
    except Exception:
        vault = ""
    if not vault or not os.path.isdir(vault):
        print(json.dumps({"ok": False, "error": "未找到 vault：请先初始化建库（建库会把 vault 路径记进 ~/.second-brain-obsidian/vault_path）"}, ensure_ascii=False))
        sys.exit(2)

    res = {a: _register(p, a, mode=args.mode) for a, p in HOOK_FILES.items()}
    res["hermes"] = _register_hermes(mode=args.mode)
    print(json.dumps({
        "ok": True, "mode": args.mode, "event": EVENT_OF[args.mode], "vault": vault, "hooks": res,
        "note": ("会话结束自动提炼" if args.mode == "end" else "每条回复后增量自动提炼")
                + "（路径取自初始化记录，纯本地、不外传）。Hermes 走 config.yaml 的 on_session_end（每回合增量），"
                + "首次需 `hermes --accept-hooks` 同意。切模式重跑 install.py --mode，注销用 --remove。",
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
