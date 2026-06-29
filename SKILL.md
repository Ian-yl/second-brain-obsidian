---
name: second-brain-obsidian
description: >-
  跨 agent 维护「你的第二大脑」（人格画像 + 知识库）到 Obsidian，用你的风格+知识复刻你。
  当用户想要：安装/初始化第二大脑、深度访谈生成画像、分析会话补充知识、加载/读取画像、
  让 AI「像我一样」回答时使用。
  触发词：第二大脑、second brain、复刻我、安装第二大脑、初始化第二大脑、
  深度对我提问、深入了解我、做人格问答、分析我的会话、加载第二大脑、设置语音密钥、
  收录链接、喂URL、整理收件箱、体检知识库。
---

# Second Brain Obsidian

把「你是谁（人格画像）+ 你知道什么（知识库）」沉淀进 Obsidian 的**统一一份** vault，
让加载它的 agent「用你的风格 + 调你的知识」做事。

**设计原则（奥卡姆 + 费曼）**：像费曼那样**先把「你是谁」讲清**（采访 → 建四层结构），再**持续补缺**。
**初始化（采访）手动触发**（用户说「深度对我提问」）；**之后在场提炼**（agent 在对话中发现新信息就直接写库）。
知识按 **Inputs / Process / Outputs / Feedback 四层**（卡帕西式）组织。

**全程 agent 直接读写 vault markdown**——建库 / 采访 / 读取 / 更新 / 知识维护都由你（agent）用自带工具（读写文件 / WebFetch）完成，**写入格式严格照 `SK/references/vault-format.md`**（去重 / 四层归类 / frontmatter 全在里面）。
**Python 给两个功能用**：语音问答（可选）和本地自动提炼（默认开，§0 自动备齐）；**核心不依赖 Python**。（`SK` = 本 skill 目录；命令里 `python3` 在 Windows 用 `python` / `py`。）

## 完整流程

```
① 安装         用户自己把这个 skill 装好
② 环境准备     §0：检测 Python → 没有就按需装 → 验证能用 → 不行就重装（语音 + 自动提炼要用；核心不依赖）
③ 初始化建库   §A：认 Obsidian（自动）→ vault 位置（用户指定 / 默认）→ 建骨架 → 记录路径到 vault_path
④ 采访写画像   §B：agent 出 6 维约 15 题 → 用户答（文字 / 语音）→ 提炼写 用户画像.md（+ 同步 CLAUDE.md/AGENTS.md）
⑤ 日常使用：
   · 读取       §读取：vault 内 CLAUDE.md（Claude）/ AGENTS.md（Codex）原生自动；别处说「加载第二大脑」
   · 更新       §自动提炼（默认开·时机=会话结束 / 每条回复 二选一）自动写本地库 + 在场提炼 + 手动「更新第二大脑」
   · 知识维护   §知识库维护：喂 URL（WebFetch）/ 整理收件箱 / 体检
   · 深度补充   §C：/insights（Claude Code）或在场提炼（Codex）
```

- **路径**：vault 位置在 ② 初始化时定一次（用户指定 or 默认）并记进 `~/.second-brain-obsidian/vault_path`；之后读取 / 更新都固定读它，不再问。
- **引擎**：全程 **agent 直接读写 Obsidian vault 的 markdown**（格式见 `vault-format.md`），**核心零 Python**；语音问答 + 本地自动提炼用 Python（**装 skill 时自动备齐，见 §0**）。

## 何时做什么

| 用户意图 | 流程 |
|---|---|
| 「安装/初始化第二大脑」「复刻我」 | A 建库 → B 采访 → 写画像 |
| 「深度对我提问 / 深入了解我 / 做人格问答」 | B1 采访（人格问答）|
| 「分析我的会话」（深度） | Claude Code：`/insights` 分析 → 入库；Codex：在场提炼（§日常维护）|
| 「收录链接 / 整理收件箱 / 体检知识库」 | 知识库维护套件（见 §知识库维护）|
| 「加载第二大脑」 | 读取画像注入（在 vault 里也原生自动）|
| 日常对话（已装好） | **读取**：vault 内原生自动（CLAUDE.md/AGENTS.md）；**更新**：自动提炼写本地库（会话结束 / 每条回复，见 §自动提炼）+ 在场提炼 |
| 「设置语音密钥」 | 见 §语音密钥（需 Python）|

---

## 0. 装 Python（安装 skill 时先做一次）

语音问答 + 本地自动提炼要用 Python（核心不依赖它）。安装时一次性备齐，**按需自动装，别让用户手配**：

1. **检测**：跑 `python3 --version`（Windows 退 `python --version` → `py --version`）。能打印版本号 → 已就绪，进 §A。
2. **没有 → 按需安装**（按本机 OS）：
   - macOS：`brew install python3`（无 brew 先装：`/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`）
   - Windows：`winget install -e --id Python.Python.3.12`
   - Linux：`sudo apt update && sudo apt install -y python3`
3. **验证能用**：再跑 `python3 --version` 且 `python3 -c "import json,os,sys,subprocess"` 都成功 = 可用。
4. **不能用 → 重装一次**（`brew reinstall python3` / 重跑 winget / `apt install --reinstall -y python3`）后再验证。仍失败 → 让用户去 https://www.python.org/downloads/ 手动装；期间核心功能照常，语音 + 自动提炼待 Python 就绪后即可用。

## A. 建库（一次）

你（agent）直接建库，按 `SK/references/vault-format.md`：
1. **认 Obsidian（自动）**：检测本机 Obsidian 装没装（mac `/Applications/Obsidian.app` 等、Win `%LOCALAPPDATA%\Programs\obsidian`）。没装 → 提示可去 https://obsidian.md（vault 是纯 markdown，不装也能读写）。
2. **库放哪**：**用户指定就用用户指定的路径；不指定就用默认**（mac=iCloud Obsidian 目录、Win=`~/Documents/second-brain`，重名加 `-2/-3`）。已有库 → 问「复用 / 新建」。
3. **建骨架 + 记录路径**：`mkdir` vault + `Knowledge/{Inputs,Process,Outputs,Feedback}` + `Inbox` + `.obsidian/app.json`（`{}`）+ 空骨架 `用户画像.md` / `CLAUDE.md`+`AGENTS.md` / `_索引.md`；**把最终 vault 绝对路径写进 `~/.second-brain-obsidian/vault_path`**（之后读取 / 自动提炼都靠它定位，不再问）。
4. 接着做人格问答（§B）写画像。
5. **开自动提炼（默认就开）→ 让用户选时机**：问用户「自动提炼什么时候做？① **会话结束**（省，一次/会话） ② **每条回复后**（实时、更稳，次数多）」→ 按选择跑 `python3 SK/scripts/install.py --mode end`（①，默认）或 `--mode stop`（②）。它读第 3 步记录的路径、注册对应本地 hook → 此后自动把对话提炼进本地 Obsidian（§0 已备好 Python）。

> Obsidian 可选：vault 就是 markdown 文件夹，装了 Obsidian 能可视化浏览（https://obsidian.md），没装也照常读写。

## B. 采访 → 写画像（费曼「先把你是谁讲清」）

**B1 人格问答** —— 初始化时、或用户说「深度对我提问」：
- **出题（agent 自己出）**：覆盖 **6 个维度**——性格特质、价值观 / 做事原则、沟通 / 说话风格、思维 / 做事方式、行为处事 / 待人接物、偏好与禁忌（**维度规范名以 `vault-format.md` 为准**，写章节标题别改字）；每维 2-3 题、共约 15 题，口语化、具体、能引出真实回答（题库思路见 `SK/references/framework.md`，别照搬种子题）。
- 问用户：**文字 还是 语音**（语音见 §语音，需 Python；没 Python 走文字）。
- **文字（默认）**：把题**一次性编号列出、让用户一条消息全填**，别逐题来回。
- **收尾**：你把答案**当场提炼**成画像，按 `vault-format.md` 写进 `用户画像.md`（6 维 + 概览 + 变更日志）并同步重写 `CLAUDE.md` + `AGENTS.md`。

**B2 四层结构** —— 建库时已建好 `Knowledge/{Inputs,Process,Outputs,Feedback}`（见 §A）。入库按四层归类：Inputs=素材/来源，Process=思考/方法/在做的，Outputs=产出/决策/结论，Feedback=复盘/教训/洞察。

## C. 分析会话（深度补充）

- **Claude Code（有 `/insights`）**：`/insights` 是内置斜杠命令（只能用户在输入框打，agent 调不了）。引导用户发 `/insights 分析我的会话`：命令生成报告落盘 `~/.claude/usage-data/report-*.html`，后半句触发本 skill 让你接管 → 你把报告 / insight 文本**直接提炼**成画像 deltas + 知识条目，按 `vault-format.md` 写进 vault（同 §日常维护）。
- **Codex（没有 `/insights`）**：会话沉淀走**在场提炼**（§日常维护，任何 agent 都行）——你在对话中发现用户新信息就直接写库；要回顾分析，让用户把要提炼的内容贴给你 / 指一个文件，你照样提炼入库。
> ❗ **不读 `~/.claude` / `~/.codex` 的原始 transcript**——只提炼用户给的内容 / `/insights` 产出。
> ⚠️ agent **运行不了** `/insights`（斜杠命令只有用户能触发）；别在代码里尝试调它。

## 知识库维护（按需）

都按四层归类、写成 `vault-format.md` 规定的笔记格式：
- **喂 URL**（用户说「收录这个链接 / 喂这个 URL」）：你用 **WebFetch** 抓 URL 正文 → 提炼 → 写进对应层 `Knowledge/<层>/<slug>.md`。
- **整理收件箱**（用户往 `<vault>/Inbox/` 丢了速记 `.md`、说「整理收件箱」）：你读 `Inbox/*.md` → 分类提炼写进 `Knowledge/<层>/` → 把原速记移到 `Inbox/_archived/`。
- **体检知识库**（用户说「体检 / lint」）：你扫所有笔记，查**断链**（`[[X]]` 指向不存在的笔记）/ **孤儿**（无入链）/ **空笔记**，报告写 `<vault>/_体检.md`。
- **索引**：每次入库后重建 `_索引.md`（顶层 MOC·按四层分组），格式见 `vault-format.md`。

## 日常维护（在场提炼）

你在对话中得知用户的**新**画像特征 / 决策 / 观点 / 方法 / 知识 / 在做的项目 / 自己搭建·运营的系统工具（现有库没有、且有长期价值）时，**主动提炼并写进 vault**——严格按 `SK/references/vault-format.md`：
- 画像 → `用户画像.md` 对应维度（去重 + 记变更日志）；
- 知识 → `Knowledge/<层>/<slug>.md`（四层归类 + 同 slug 合并）；
- 改完**同步重写** `CLAUDE.md` + `AGENTS.md` + `_索引.md`。
**任何话题都收**（含搭建本系统、项目、闲聊里的真实信息）——只要关于用户、有保留价值；唯一例外：明文密钥 / token 脱敏不写。你本就有对话上下文，直接提炼直接写。用户说「更新第二大脑」时一并补全。
> 深度分析走 `/insights`（§C）。**自动提炼默认就开**（时机=会话结束 / 每条回复，见 §自动提炼）——在场提炼是它之外的即时补充。

## 自动提炼（默认开·纯本地，写进你的 Obsidian）

**默认就开**（§A 第 5 步注册本地 hook；路径取自初始化记录）。**两种时机，初始化时让用户选**：
- **会话结束（`--mode end`，默认）**：SessionEnd 触发，读**整段**对话一次提炼。省（一次/会话）。
- **每条回复后（`--mode stop`）**：Stop 触发，**增量**只提炼上次之后的新内容（进度标记防重复）。实时、更稳（会话没正常结束也不丢），但次数多。
> 两者**收的内容一样全**，差在时机 + 成本。切换：重跑 `install.py --mode end|stop`（自动清旧的，不留两份）。Stop 在 Claude Code 完整支持；Codex 若无 Stop 钩子就用 end。

触发后，后台用 `claude -p` / `codex exec`（**带 `--strict-mcp-config`，不加载任何 MCP**）读对话、按 `vault-format.md` 提炼进你的本地 vault。
- **收什么**：关于用户、有保留价值的都收——**任何话题都不跳过**（含搭建本系统、项目、闲聊）；唯一例外：明文密钥 / token 脱敏不写。
- **纯本地、零外传**：只写你电脑里的 Obsidian markdown，不上传任何东西。和 HelixMesh 无关（它只是下载本 skill 的平台）。
- 需要 **Python** + `claude`/`codex` CLI（默认 haiku 省钱）——§0 已自动备齐。防递归：`SBO_PROCESSING` 护栏。
- 关掉：`python3 SK/scripts/install.py --remove`。

## 读取（注入画像）

- **vault 内·原生自动**：vault 根 `CLAUDE.md`（Claude Code）/ `AGENTS.md`（Codex）（两份同内容、画像每次同步重写）——在 vault 目录开对应 agent **原生自动读**。这是默认读取方式。
- **任何项目里·手动**：用户说「加载第二大脑」→ 你读 `<vault>/用户画像.md` + 相关 `Knowledge/` 笔记，注入上下文「像用户一样」回答。

## 语音问答（打电话式·需 Python）

> **语音是唯一用到 Python 的功能**（本地 Azure STT 桥）。没探测到 Python → 告诉用户「语音要 Python 环境，咱们先走文字问答」，其余功能照常。

用户选语音且有 Python 时：
1. `python3 SK/scripts/keys.py status` 确认 Azure 已配（没配就引导配密钥，或回退文字）。
2. 把这轮问题存 `/tmp/q.json`（`["问题1",...]`）。
3. `python3 SK/scripts/voice/bridge.py --questions /tmp/q.json --out /tmp/answers.json --background`
   —— **必须加 `--background`**（不加是前台 serve、会一直卡住你）。它**秒返回 URL**、自动开浏览器；
   把 URL 以**可点击 markdown 链接**发给用户（如 `[🎙️ 打开语音问答](http://127.0.0.1:8765/)`），
   说明会自动弹浏览器、没弹就点链接，然后点页面的「开始通话」。
4. 浏览器**像打电话**：MiniMax 音色自动朗读（页面右上角可选**男声 / 女声**，默认女声）→ 自动聆听 → 停顿即下一题；**同步显示文字 + 对话历史**。
5. **等用户说「答完了」**（或 `/tmp/answers.json` 写出后）→ 你读 `answers` **直接提炼写画像**（同 §B 收尾）。
   - `/tmp/answers.json` 带 **`reason`**：`completed`(答完) / `hangup`(主动结束) → 正常入库；
     **`error` / `closed`（异常 / 中途关页面）→ 告诉用户「语音异常结束」，问要不要重试或转文字**，别当成功。

## 语音密钥（随时设置·需 Python）

- `python3 SK/scripts/keys.py status` 看现状；`keys.py set --azure-key <KEY> [--azure-region koreacentral] [--minimax-key <KEY>]`。
- 必需 Azure STT；可选 MiniMax（更自然音色，不填用浏览器 TTS）。密钥仅存 `~/.second-brain-obsidian/secrets.env`（chmod 600）。

---

## Python 文件（核心不依赖）

- **语音问答（可选）**：`scripts/voice/bridge.py` + `scripts/voice/web/index.html`（打电话式 STT + 对话历史）、`scripts/keys.py`（语音密钥，存 `~/.second-brain-obsidian/secrets.env`，chmod 600）、`scripts/store.py`（语音小工具）。
- **本地自动提炼（默认开）**：`scripts/install.py`（注册本地 hook：SessionEnd 或 Stop 两模式 + 记 vault 路径）、`scripts/hook_entry.py`（对话提炼写**本地** vault，纯本地、不外传）。

核心功能（建库 / 采访 / 读取 / 在场更新 / 知识维护）全是 agent 直接读写 vault markdown，按 `references/vault-format.md`，**不依赖 Python**。Python 给：语音问答（可选）+ 本地自动提炼（默认开，§0 自动备齐）。

## 注意

- **建库 / 采访 / 读取 / 更新 / 知识维护**：agent 直接读写 vault markdown 完成（格式见 `vault-format.md`）。语音问答用 Python。
- **初始化手动，之后在场提炼**：采访手动触发；日常对话中 agent 发现新信息就按 `vault-format.md` 直接写库。深度补充走 `/insights`。
- **知识四层**：Inputs / Process / Outputs / Feedback（卡帕西式），入库归类。
- **隐私**：全程本地；语音密钥仅在 `secrets.env`，绝不进 vault/git；提炼时对密钥/token 脱敏（别写进库）。
- **统一一份**：所有 agent 共享同一 vault 的同一份画像 + 知识。
- **跨平台（mac / Windows）**：默认库位置 mac=iCloud Obsidian 目录、Win=`~/Documents`；语音后台派生两平台都适配；命令里 `python3` 在 Win 用 `python` / `py`。
