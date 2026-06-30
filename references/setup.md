# 安装与配置

> 建库 / 采访 / 读取 / 更新 / 知识维护由 agent 直接读写 vault markdown 完成（格式见 `vault-format.md`，这部分不靠 Python）。**但需要 Python——本地自动提炼（默认开）+ 语音问答都靠它；安装 skill 时 agent 自动检测并按需装好（检测 → 装 → 验证 → 不行重装），你无需手配。**

## 1. 前提
- 一个支持的 agent：**Claude Code / Codex / Hermes**。
- （可选）**Obsidian**：vault 就是 markdown 文件夹，装了能可视化浏览（https://obsidian.md），没装也照常读写。
- **Python 3.8+**（本地自动提炼默认开 + 语音问答都要用）：**安装 skill 时 agent 自动检测，没有就按需装、装完验证、不行重装**——你不用手动配。失败兜底：手动装 https://www.python.org/downloads/（Win 也可 Microsoft Store）。
- 系统 macOS / Windows 都支持。

## 2. 建库（agent 直接做）
在 agent 对话里说「安装第二大脑 / 初始化第二大脑」，agent 会：
- 问你库放哪（默认 mac=iCloud Obsidian 目录、Win=`~/Documents/second-brain`，或你指定）；
- 按 `vault-format.md` 建 vault：`00-Home.md` + 一级目录（`00-Inbox 10-Inputs 20-Process 30-Outputs 40-Feedback 50-MOCs 60-Domains 70-Assets 90-Archive _System`）+ `50-MOCs/` 六张 MOC + `.obsidian/` + 空骨架 `用户画像.md` / `CLAUDE.md` + `AGENTS.md`（二级中文工作模式子目录、行业页按需建）；
- 然后做人格问答（采访）写画像；
- **默认开启本地自动提炼**（初始化时选时机：会话结束 / 每条回复）：注册本地 hook（Claude/Codex 写各自 settings；**Hermes** 写 `~/.hermes/config.yaml`：end→`on_session_finalize`（整会话一次）/ stop→`on_session_end`（每回合），首次需 `hermes --accept-hooks` 同意）→ 自动把对话提炼进本地 vault（纯本地、不外传；需 Python，已自动备好）。切换/关：`install.py --mode end|stop` / `--remove`。
> 在 vault 目录里开 Claude Code 会**原生自动读 `CLAUDE.md`**、Codex / Hermes 读 `AGENTS.md`（两份同内容）——这就是默认的「读取注入」。

## 3. 语音问答密钥（仅语音·需 Python）
实时语音作答需微软 Azure STT。配密钥：`python3 <skill>/scripts/keys.py set --azure-key <KEY> [--azure-region koreacentral] [--minimax-key <KEY>]`，或手写进 `~/.second-brain-obsidian/secrets.env`（chmod 600）：
```
AZURE_SPEECH_KEY=你的-azure-subscription-key
AZURE_SPEECH_REGION=koreacentral
# TTS（可选，MiniMax）：
MINIMAX_API_KEY=你的-minimax-key
MINIMAX_API_HOST=https://api.minimax.chat
```
> 密钥**只**放这里，绝不进 vault / git / 文档，权限设 600。

启动语音：`python3 <skill>/scripts/voice/bridge.py --questions <q.json> --out <answers.json> --background`，浏览器打开它打印的 URL（Windows 把 `python3` 换成 `python` / `py`）。
> **音色**：页面右上角可选**男声 / 女声**（默认女声）；想固定自定义音色可在 `secrets.env` 设 `MINIMAX_VOICE_ID`（页面选择优先于它）。

## 4. 卸载
删掉 vault 目录 + `~/.second-brain-obsidian/`（语音密钥）即可。
