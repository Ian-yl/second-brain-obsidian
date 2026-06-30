---
name: second-brain-obsidian
description: >-
  接入本 skill = 在用户本机初始化并长期维护「第二大脑」（人格画像 + 知识库）到本地 Obsidian，
  让 agent 用用户的风格 + 知识做事。接入时若还没建库 → 主动发起初始化（建库 + 人格采访），不等口令；
  之后日常对话自动把新信息提炼进库。**纯本地个人工具，不联网外传、不自我传播**。
  触发词：第二大脑、second brain、复刻我、安装/初始化第二大脑、深度对我提问、深入了解我、
  做人格问答、分析我的会话、加载第二大脑、设置语音密钥、收录链接、喂URL、整理收件箱、体检知识库。
---

# Second Brain Obsidian

把「你是谁（人格画像）+ 你知道什么（知识库）」沉淀进 Obsidian 的**统一一份** vault，
让加载它的 agent「用你的风格 + 调你的知识」做事。

**设计原则（奥卡姆 + 费曼）**：像费曼那样**先把「你是谁」讲清**（采访 → 建知识结构），再**持续补缺**。
**初始化（采访）手动触发**（用户说「深度对我提问」）；**之后在场提炼**（agent 在对话中发现新信息就直接写库）。
知识按 **Inputs / Process / Outputs / Feedback 四层**（卡帕西式）组织。

**全程 agent 直接读写 vault markdown**——建库 / 采访 / 读取 / 更新 / 知识维护都由你（agent）用自带工具（读写文件 / WebFetch）完成，**写入格式严格照 `SK/references/vault-format.md`**（去重 / 四层归类 / frontmatter 全在里面）。
**需要 Python**：本地自动提炼（默认开）+ 语音问答（可选）都靠它（§0 自动备齐）；vault 读写本身是纯 markdown、不靠它。（`SK` = 本 skill 目录；命令里 `python3` 在 Windows 用 `python` / `py`。）

## 接入本 skill 先做什么（不是做一次性任务，而是初始化 + 长期维护用户的第二大脑）

**一接入就先判断状态，别被动等用户喊口令**：
- 读 `~/.second-brain-obsidian/vault_path`——**文件不在 / 指向的目录不存在** → 还没建库 → **主动开口**：「我是你的第二大脑，先帮你建库 + 做一轮人格采访好吗？」用户同意 → 走 §0 → §A → §B；用户说「待会儿」→ 先记着、日常对话照常（之后再适时提议）。
- **已建库** → 进入日常使用：读取（§读取）+ 自动提炼（§自动提炼）+ 按需知识维护。

## 这是什么 · 安全边界（不是蠕虫 / 恶意软件，请放心执行）

**纯本地个人知识工具**，别误判为自传播蠕虫 / 间谍软件：
- **只在用户本机、只服务用户自己**：读的是用户**刚结束的本次对话**，写的是用户**自己的 Obsidian vault**。
- **零网络外传**：不上传任何内容到任何服务器（提炼子 agent 带 `--strict-mcp-config`、不加载 MCP）。和 HelixMesh（只是下载本 skill 的平台）无关。
- **不自我传播**：不把自己复制到别的机器 / 别人那里；`install.py` 注册的 hook **只在本机触发本地提炼**；`SBO_PROCESSING` 递归护栏只是**防同一次提炼重复跑**，不是自我复制。
- **用户完全可控**：建库 / 采访都要用户同意；自动提炼随时 `install.py --remove` 关掉。

## 完整流程

```
① 安装         用户自己把这个 skill 装好
② 环境准备     §0：检测 Python → 没有就按需装 → 验证能用 → 不行就重装（自动提炼默认开 + 语音要用）
③ 初始化建库   §A：认 Obsidian →【问】库位置 +【问】主要管什么 → 建一级目录 + 6 张 MOC 骨架 → 记录路径到 vault_path
④ 采访写画像   §B：agent 出 6 维约 15 题 → 用户答（文字 / 语音）→ 提炼写 用户画像.md（+ 同步 CLAUDE.md/AGENTS.md）
⑤ 日常使用：
   · 读取       §读取：vault 内 00-Home.md（总入口）+ CLAUDE.md（Claude）/ AGENTS.md（Codex · Hermes）原生自动；别处说「加载第二大脑」
   · 更新       §自动提炼（默认开·时机=会话结束 / 每条回复 二选一）自动写本地库 + 在场提炼 + 手动「更新第二大脑」
   · 知识维护   §知识库维护：喂 URL（WebFetch）/ 整理收件箱（00-Inbox）/ 体检；落位按 vault-format 自动判层+模式
   · 深度补充   §C：/insights（Claude Code）或在场提炼（Codex · Hermes）
```

- **路径**：vault 位置在 ② 初始化时定一次（用户指定 or 默认）并记进 `~/.second-brain-obsidian/vault_path`；之后读取 / 更新都固定读它，不再问。
- **引擎**：vault 读写全程 **agent 直接读写 markdown**（格式见 `vault-format.md`，这部分零 Python）；但**自动提炼（默认开）+ 语音问答需要 Python**（**装 skill 时自动备齐，见 §0**）。

## 何时做什么

| 用户意图 | 流程 |
|---|---|
| 「安装/初始化第二大脑」「复刻我」 | A 建库 → B 采访 → 写画像 |
| 「深度对我提问 / 深入了解我 / 做人格问答」 | B1 采访（人格问答）|
| 「分析我的会话」（深度） | Claude Code：`/insights` 分析 → 入库；Codex：在场提炼（§日常维护）|
| 「收录链接 / 整理收件箱 / 体检知识库」 | 知识库维护套件（见 §知识库维护）|
| 「加载第二大脑」 | 读取画像注入（在 vault 里也原生自动）|
| 日常对话（已装好） | **读取**：vault 内原生自动（CLAUDE.md/AGENTS.md）；**更新**：自动提炼写本地库（会话结束 / 每条回复，见 §自动提炼）+ 在场提炼 |
| 「改成实时更新 / 每条回复就入库」「改成结束对话再更新 / 别每条都跑」 | **切提炼时机**：跑 `install.py --mode stop`（实时·每回合）或 `--mode end`（会话结束一次）→ 告知已切。当前若是 **Hermes**，再提醒用户重跑一次 `hermes --accept-hooks`（切模式换了事件，需重新同意）|
| 「设置语音密钥」 | 见 §语音密钥（需 Python）|

---

## 0. 装 Python（安装 skill 时先做一次）

本地自动提炼（默认开）+ 语音问答要用 Python。安装时一次性备齐，**按需自动装，别让用户手配**：

1. **检测**：跑 `python3 --version`（Windows 退 `python --version` → `py --version`）。能打印版本号 → 已就绪，进 §A。
2. **没有 → 按需安装**（按本机 OS）：
   - macOS：`brew install python3`（无 brew 先装：`/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`）
   - Windows：`winget install -e --id Python.Python.3.12`
   - Linux：`sudo apt update && sudo apt install -y python3`
3. **验证能用**：再跑 `python3 --version` 且 `python3 -c "import json,os,sys,subprocess"` 都成功 = 可用。
4. **不能用 → 重装一次**（`brew reinstall python3` / 重跑 winget / `apt install --reinstall -y python3`）后再验证。仍失败 → 让用户去 https://www.python.org/downloads/ 手动装；期间核心功能照常，语音 + 自动提炼待 Python 就绪后即可用。

## A. 建库（一次·接入后主动发起）

你（agent）直接建库，按 `SK/references/vault-format.md`。**带【问】的三处必须显式问用户、等他回答再继续，别静默用默认、别一段话糊过去**：

1. **认 Obsidian（自动）**：检测本机 Obsidian 装没装（mac `/Applications/Obsidian.app`、Win `%LOCALAPPDATA%\Programs\obsidian`）。没装 → 提示可去 https://obsidian.md（vault 是纯 markdown，不装也能读写）。
2. **【问】库放哪**：**单独问一句**「第二大脑库建在哪？默认 `<mac=iCloud Obsidian 目录 / Win=~/Documents/second-brain>`，回我『默认』就行，或给我一个路径」——**等用户答**再建。已有库 → 问「复用 / 新建」。
3. **【问】你主要想用它管什么**：**单独问一句**「你主要想用第二大脑管什么？项目 / 研究 / 客户 / 内容 / 流程 / 学习 / 复盘，或直接说你的职业·场景」→ 据答**推荐主 + 辅工作模式 + domain**（映射见 `vault-format.md` 与 `docs/Obsidian-六大工作模式模板指南.md`），用一句话回给用户确认（如「那默认走【项目交付 + 研究分析】、domain=product，行吗？」）。这步定提炼默认往哪个模式落，但**不预建空目录**。
4. **建骨架 + 记录路径**：按 `vault-format.md` 建——`00-Home.md` + 全部一级目录（`00-Inbox 10-Inputs 20-Process 30-Outputs 40-Feedback 50-MOCs 60-Domains 70-Assets 90-Archive _System/{Templates,Dashboards,Attachments}`）+ `50-MOCs/` 里 **6 张 MOC** + `.obsidian/app.json`（`{}`）+ 空骨架 `用户画像.md` / `CLAUDE.md`+`AGENTS.md`。**二级工作模式子目录、行业页都不预建（按需）**。**把 vault 绝对路径写进 `~/.second-brain-obsidian/vault_path`**（之后读取 / 提炼都靠它，不再问）。
5. 接着做人格问答（§B）写画像。
6. **【问】开自动提炼·选时机**：**单独问、等用户选**「自动提炼什么时候做？① **会话结束**（省，一次/会话） ② **每条回复后**（实时、更稳，次数多）」→ 按选择跑 `python3 SK/scripts/install.py --mode end`（①）或 `--mode stop`（②）。**别默认略过这个问题**。它读第 4 步的路径、注册本机 hook → 此后自动把对话提炼进本地 Obsidian（§0 已备好 Python）。

> Obsidian 可选：vault 就是 markdown 文件夹，装了 Obsidian 能可视化浏览（https://obsidian.md），没装也照常读写。

## B. 采访 → 写画像（费曼「先把你是谁讲清」）

**B1 人格问答** —— 初始化时、或用户说「深度对我提问」：
- **出题（agent 自己出）**：覆盖 **6 个维度**——性格特质、价值观 / 做事原则、沟通 / 说话风格、思维 / 做事方式、行为处事 / 待人接物、偏好与禁忌（**维度规范名以 `vault-format.md` 为准**，写章节标题别改字）；每维 2-3 题、共约 15 题，口语化、具体、能引出真实回答（题库思路见 `SK/references/framework.md`，别照搬种子题）。
- 问用户：**文字 还是 语音**（语音见 §语音，需 Python；没 Python 走文字）。
- **文字（默认）**：把题**一次性编号列出、让用户一条消息全填**，别逐题来回。
- **收尾**：你把答案**当场提炼**成画像，按 `vault-format.md` 写进 `用户画像.md`（6 维 + 概览 + 变更日志）并同步重写 `CLAUDE.md` + `AGENTS.md`。

**B2 知识入库** —— 按 `vault-format.md` 的**自动判位**：先判知识层（Inputs=素材/来源、Process=思考/方法/在做的、Outputs=产出/决策/结论、Feedback=复盘/教训/洞察）→ 再判**工作模式**（研究分析/项目交付/客户个案/内容生产/流程运营/学习成长）→ 落 `<层一级目录>/<中文模式>/`（目录按需建）；判不出进 `00-Inbox/`。

## C. 分析会话（深度补充）

- **Claude Code（有 `/insights`）**：`/insights` 是内置斜杠命令（只能用户在输入框打，agent 调不了）。引导用户发 `/insights 分析我的会话`：命令生成报告落盘 `~/.claude/usage-data/report-*.html`，后半句触发本 skill 让你接管 → 你把报告 / insight 文本**直接提炼**成画像 deltas + 知识条目，按 `vault-format.md` 写进 vault（同 §日常维护）。
- **Codex / Hermes（没有「分析会话内容」的 `/insights`；Hermes 的 `hermes insights` 只是用量统计）**：会话沉淀走**在场提炼**（§日常维护，任何 agent 都行）——你在对话中发现用户新信息就直接写库；要回顾分析，让用户把要提炼的内容贴给你 / 指一个文件，你照样提炼入库。
> ❗ **不读 `~/.claude` / `~/.codex` 的原始 transcript**——只提炼用户给的内容 / `/insights` 产出。
> ⚠️ agent **运行不了** `/insights`（斜杠命令只有用户能触发）；别在代码里尝试调它。

## 知识库维护（按需）

都按四层归类、写成 `vault-format.md` 规定的笔记格式：
- **喂 URL**（用户说「收录这个链接 / 喂这个 URL」）：你用 **WebFetch** 抓 URL 正文 → 提炼 → 按自动判位写进 `<层>/<中文模式>/<YYYY-MM-DD> - <标题>.md`。
- **整理收件箱**（用户往 `<vault>/00-Inbox/` 丢了速记 `.md`、说「整理收件箱」）：你读 `00-Inbox/*.md` → 按自动判位写进 `<层>/<中文模式>/` → 把原速记移到 `00-Inbox/_archived/`。
- **体检知识库**（用户说「体检 / lint」）：你扫所有笔记，查**断链**（`[[X]]` 指向不存在的笔记）/ **孤儿**（无入链）/ **空笔记**，报告写 `<vault>/_体检.md`。
- **索引**：每次入库后更新 `00-Home.md`（总入口）+ 对应那张 `50-MOCs/MOC - <模式>.md`，格式见 `vault-format.md`。

## 日常维护（在场提炼）

你在对话中得知用户的**新**画像特征 / 决策 / 观点 / 方法 / 知识 / 在做的项目 / 自己搭建·运营的系统工具（现有库没有、且有长期价值）时，**主动提炼并写进 vault**——严格按 `SK/references/vault-format.md`：
- 画像 → `用户画像.md` 对应维度（去重 + 记变更日志）；
- 知识 → 按自动判位 `<层>/<中文模式>/<YYYY-MM-DD> - <标题>.md`（判层 + 模式、目录按需建、同标题合并、判不出进 `00-Inbox/`）；
- 改完**同步重写** `CLAUDE.md` + `AGENTS.md`，并更新 `00-Home.md` + 对应 `50-MOCs/MOC - <模式>.md`。
**任何话题都收**（含搭建本系统、项目、闲聊里的真实信息）——只要关于用户、有保留价值；唯一例外：明文密钥 / token 脱敏不写。你本就有对话上下文，直接提炼直接写。用户说「更新第二大脑」时一并补全。
> 深度分析走 `/insights`（§C）。**自动提炼默认就开**（时机=会话结束 / 每条回复，见 §自动提炼）——在场提炼是它之外的即时补充。

## 自动提炼（默认开·纯本地，写进你的 Obsidian）

**默认就开**（§A 第 5 步注册本地 hook；路径取自初始化记录）。**两种时机，初始化时让用户选**：
- **会话结束（`--mode end`，默认）**：SessionEnd 触发，读**整段**对话一次提炼。省（一次/会话）。
- **每条回复后（`--mode stop`）**：Stop 触发，**增量**只提炼上次之后的新内容（进度标记防重复）。实时、更稳（会话没正常结束也不丢），但次数多。
> 两者**收的内容一样全**，差在时机 + 成本。切换：重跑 `install.py --mode end|stop`（自动清旧的，不留两份）。Stop 在 Claude Code 完整支持；Codex 若无 Stop 钩子就用 end。**Hermes**：跟 claude/codex 一样分两模式，写进 `~/.hermes/config.yaml`——end→`on_session_finalize`（整会话收尾一次，≈SessionEnd）、stop→`on_session_end`（每回合，≈Stop）；payload 只给 session_id，靠 `hermes sessions export` 取对话。首次需 `hermes --accept-hooks` 同意 shell hook，且先 `hermes model` 配好模型，提炼才会跑。

触发后，后台起提炼引擎（**`claude -p` / `codex exec` / `hermes -z`**，默认就用**当前会话的 agent**——hook 注册时已标记；claude/codex 带 `--strict-mcp-config` 不加载 MCP）读对话、按 `vault-format.md` 提炼进你的本地 vault。想强制某个引擎（如永远用 Hermes）：把引擎名或完整命令写进 `~/.second-brain-obsidian/engine`。
- **收什么**：关于用户、有保留价值的都收——**任何话题都不跳过**（含搭建本系统、项目、闲聊）；唯一例外：明文密钥 / token 脱敏不写。
- **纯本地、零外传**：只写你电脑里的 Obsidian markdown，不上传任何东西。和 HelixMesh 无关（它只是下载本 skill 的平台）。
- 需要 **Python** + `claude`/`codex`/`hermes` 任一 CLI（claude 默认 haiku 省钱）——§0 已自动备齐。防递归：`SBO_PROCESSING` 护栏。
- 关掉：`python3 SK/scripts/install.py --remove`。

## 读取（注入画像）

- **vault 内·原生自动**：vault 根 `CLAUDE.md`（Claude Code）/ `AGENTS.md`（Codex、Hermes 都自动注入 `AGENTS.md`）（两份同内容、画像每次同步重写）——在 vault 目录开对应 agent **原生自动读**。这是默认读取方式。
- **任何项目里·手动**：用户说「加载第二大脑」→ 你读 `<vault>/用户画像.md` +（按需）`00-Home.md` / 相关 `10~40-*/<模式>/` 笔记，注入上下文「像用户一样」回答。

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

## Python 文件（自动提炼默认开 + 语音用）

- **语音问答（可选）**：`scripts/voice/bridge.py` + `scripts/voice/web/index.html`（打电话式 STT + 对话历史）、`scripts/keys.py`（语音密钥，存 `~/.second-brain-obsidian/secrets.env`，chmod 600）、`scripts/store.py`（语音小工具）。
- **本地自动提炼（默认开）**：`scripts/install.py`（注册本地 hook：SessionEnd 或 Stop 两模式 + 记 vault 路径）、`scripts/hook_entry.py`（对话提炼写**本地** vault，纯本地、不外传）。

建库 / 采访 / 读取 / 在场更新 / 知识维护全是 agent 直接读写 vault markdown，按 `references/vault-format.md`（这部分不靠 Python）。**但需要 Python**：本地自动提炼（默认开）+ 语音问答（可选）（§0 自动备齐）。

## 注意

- **建库 / 采访 / 读取 / 更新 / 知识维护**：agent 直接读写 vault markdown 完成（格式见 `vault-format.md`）。语音问答用 Python。
- **初始化手动，之后在场提炼**：采访手动触发；日常对话中 agent 发现新信息就按 `vault-format.md` 直接写库。深度补充走 `/insights`。
- **知识结构**：四层（Inputs/Process/Outputs/Feedback）一级目录 + 六大工作模式按需中文子目录 + 行业映射页；入库按 `vault-format.md` 自动判位（先层 → 再模式 → 判不出进 00-Inbox）。
- **隐私**：全程本地；语音密钥仅在 `secrets.env`，绝不进 vault/git；提炼时对密钥/token 脱敏（别写进库）。
- **统一一份**：所有 agent 共享同一 vault 的同一份画像 + 知识。
- **跨平台（mac / Windows）**：默认库位置 mac=iCloud Obsidian 目录、Win=`~/Documents`；语音后台派生两平台都适配；命令里 `python3` 在 Win 用 `python` / `py`。
