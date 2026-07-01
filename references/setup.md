# 安装与配置

> 建库 / 采访 / 读取 / 提炼 / 知识维护全由 agent 直接读写 vault markdown 完成（格式见 `vault-format.md`）——**零依赖、不装 hook、不跑后台进程**。**唯一用到 Python 的是可选的语音问答**；不用语音就完全不需要 Python。

## 1. 前提
- 一个支持的 agent：**Claude Code / Codex / Hermes**。
- （可选）**Obsidian**：vault 就是 markdown 文件夹，没装也照常读写。建库时 agent 可帮你装（mac `brew install --cask obsidian` / Win `winget install -e --id Obsidian.Obsidian` / Linux flatpak），或去 https://obsidian.md 手动。
- （可选）**Python 3.8+**：**仅在用语音问答时需要**（本地 Azure STT 桥）；用语音再装即可（mac `brew install python3` / Win `winget install -e --id Python.Python.3.12` / 手动 https://www.python.org/downloads/）。**不用语音完全不需要 Python。**
- 系统 macOS / Windows 都支持。

## 2. 建库（agent 直接做）
在 agent 对话里说「安装第二大脑 / 初始化第二大脑」，agent 会：
- 问你库放哪（默认 mac=iCloud Obsidian 目录、Win=`~/Documents/second-brain`，或你指定）；
- 按 `vault-format.md` 建 vault：`00-Home.md` + 一级目录（`00-Inbox 10-Inputs 20-Process 30-Outputs 40-Feedback 50-MOCs 60-Domains 70-Assets 90-Archive _System`）+ `50-MOCs/` 六张 MOC + `.obsidian/` + 空骨架 `用户画像.md` / `CLAUDE.md` + `AGENTS.md`（二级中文工作模式子目录、行业页按需建），并把库路径写进 `~/.second-brain-obsidian/vault_path`；
- 然后做人格问答（采访）写画像。
- **之后日常对话靠 agent 每轮「在场提炼」自动写库**——发现关于你的新信息就按 `vault-format.md` 写进 vault（**提示词驱动，无需安装 / 注册任何东西、不装 hook、不跑后台**）。
> 在 vault 目录里开 Claude Code 会**原生自动读 `CLAUDE.md`**、Codex / Hermes 读 `AGENTS.md`（两份同内容）——这就是默认的「读取注入」。

## 3. 语音问答密钥（仅语音·需 Python）
实时语音作答需 **Azure STT（听·必需）+ 推荐 MiniMax（读·朗读更自然，不配回退浏览器朗读）**——两个都建议配。配密钥：`python3 <skill>/scripts/keys.py set --azure-key <KEY> [--azure-region koreacentral] [--minimax-key <KEY>]`，或手写进 `~/.second-brain-obsidian/secrets.env`（chmod 600）：
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
删掉 vault 目录 + `~/.second-brain-obsidian/`（语音密钥）即可。**本版没注册任何 hook / 后台进程，无需额外卸载。**
