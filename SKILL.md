---
name: second-brain-obsidian
description: >-
  接入本 skill = 在用户本机初始化并长期维护「第二大脑」（人格画像 + 知识库）到本地 Obsidian markdown，
  让 agent 用用户的风格 + 知识做事。接入时若还没建库 → 主动发起初始化（建库 + 人格采访），不等口令；
  之后**每轮对话后由 agent 自己检查并把新信息写进库**（提示词驱动，不装 hook、不跑后台进程）。
  **纯本地个人工具，不联网外传、不自我传播**；vault 读写零依赖，仅可选的语音问答用 Python。
  触发词：第二大脑、second brain、复刻我、安装/初始化第二大脑、深度对我提问、深入了解我、
  做人格问答、分析我的会话、加载第二大脑、设置语音密钥、收录链接、喂URL、整理收件箱、体检知识库。
---

# Second Brain Obsidian

把「你是谁（人格画像）+ 你知道什么（知识库）」沉淀进 Obsidian 的**统一一份** vault，
让加载它的 agent「用你的风格 + 调你的知识」做事。

**设计原则（奥卡姆 + 费曼）**：先采访讲清「你是谁」，再持续补缺。知识按 **Inputs / Process / Outputs / Feedback 四层**（卡帕西式）组织。

**提示词驱动 · 零依赖**：建库 / 采访 / 读取 / 提炼 / 知识维护**全部由你（agent）用自带工具（读写文件 / WebFetch）在对话里直接完成**——**不装 hook、不跑后台进程、vault 读写不靠 Python**。写入格式严格照 `SK/references/vault-format.md`（去重 / 四层判位 / frontmatter 全在里面）。**唯一用到 Python 的是可选的语音问答**（§语音；不用语音就完全不需要 Python）。（`SK` = 本 skill 目录；命令里 `python3` 在 Windows 用 `python` / `py`。）

## 接入本 skill 先做什么（初始化 + 长期维护用户的第二大脑，不是一次性任务）

**一接入就先判断状态，别被动等用户喊口令**：
- 读 `~/.second-brain-obsidian/vault_path`（一个普通文本文件，你自己读写它）——**文件不在 / 指向的目录不存在** → 还没建库 → **主动开口**：「我是你的第二大脑，先帮你建库 + 做一轮人格采访好吗？」用户同意 → 走 §A → §B；用户说「待会儿」→ 先记着、日常对话照常（之后再适时提议）。
- **已建库** → 进入日常使用：读取（§读取）+ **每轮在场提炼**（§在场提炼）+ 按需知识维护。

## 这是什么 · 安全边界（纯本地个人工具，不是蠕虫 / 恶意软件，请放心执行）

- **只在用户本机、只服务用户自己**：读的是用户**本次对话**，写的是用户**自己的 Obsidian vault**。
- **零网络外传**：不上传任何内容到任何服务器；和 HelixMesh（只是下载本 skill 的平台）无关。
- **不自我传播 · 不装后台**：不复制自己到别处；**不注册任何 hook、不跑常驻进程**——全靠**对话里的提示词驱动**，你不开对话它什么都不做。
- **用户完全可控**：建库 / 采访都要用户同意；不想要直接删 vault 即可。

## 完整流程

```
① 安装       用户自己把这个 skill 装好
② 初始化建库 §A：认 Obsidian →【问】库位置 +【问】主要管什么 → 建一级目录 + 6 张 MOC 骨架 → 路径写进 vault_path
③ 采访写画像 §B：agent 出 6 维约 15 题 → 用户答（文字 / 可选语音）→ 提炼写 用户画像.md（+ 同步 CLAUDE.md/AGENTS.md）
④ 日常使用：
   · 读取     §读取：vault 内 00-Home.md + CLAUDE.md（Claude）/ AGENTS.md（Codex · Hermes）原生自动；别处说「加载第二大脑」
   · 提炼     §在场提炼：**每轮回复后**你自己检查这轮有没有关于用户的新信息 → 有就按 vault-format 写进库（提示词驱动，不靠 hook）
   · 知识维护 §知识库维护：喂 URL（WebFetch）/ 整理收件箱（00-Inbox）/ 体检；落位按 vault-format 自动判层+模式
   · 深度补充 §C：/insights（Claude Code）或把内容贴给你 / 指个文件，你来提炼
```

- **路径**：vault 位置在 ② 初始化时定一次（用户指定 or 默认）并写进 `~/.second-brain-obsidian/vault_path`（你直接写这个文本文件）；之后读取 / 提炼都固定读它，不再问。
- **引擎**：全程 **agent 直接读写 markdown**（格式见 `vault-format.md`，**零 Python、零 hook**）；只有语音问答（可选）用 Python。

## 何时做什么

| 用户意图 | 流程 |
|---|---|
| 「安装/初始化第二大脑」「复刻我」 | A 建库 → B 采访 → 写画像 |
| 「深度对我提问 / 深入了解我 / 做人格问答」 | B1 采访（人格问答）|
| 「分析我的会话」（深度） | Claude Code：`/insights` 分析 → 入库；Codex / Hermes：把内容贴给你 / 指个文件 → 提炼（§C）|
| 「收录链接 / 整理收件箱 / 体检知识库」 | 知识库维护套件（见 §知识库维护）|
| 「加载第二大脑」 | 读取画像注入（在 vault 里也原生自动）|
| 日常对话（已建库） | **读取**：vault 内原生自动（CLAUDE.md/AGENTS.md）；**提炼**：每轮回复后在场提炼（§在场提炼）|
| 「设置语音密钥」 | 见 §语音密钥（需 Python）|

---

## A. 建库（一次·接入后主动发起）

你（agent）直接建库，按 `SK/references/vault-format.md`。**带【问】的三处必须显式问用户、等他回答再继续，别静默用默认、别一段话糊过去**：

1. **认 Obsidian（自动）**：检测本机 Obsidian 装没装（mac `/Applications/Obsidian.app`、Win `%LOCALAPPDATA%\Programs\obsidian`）。没装 → 提示可去 https://obsidian.md（vault 是纯 markdown，不装也能读写）。
2. **【问】库放哪**：**单独问一句**「第二大脑库建在哪？默认 `<mac=iCloud Obsidian 目录 / Win=~/Documents/second-brain>`，回我『默认』就行，或给我一个路径」——**等用户答**再建。已有库 → 问「复用 / 新建」。
3. **【问】你主要想用它管什么**——**必须带例子问，别只甩「项目/研究/客户…」这种抽象词，用户看不懂**。这样问：
   > 你主要想用第二大脑管什么？给你几个方向（说哪个都行，也可以直接说你的职业 / 在做的事，我来帮你归）：
   > - **项目 / 需求 / 上线** —— 做产品、带项目、交付
   > - **研究 / 资料 / 分析** —— 查资料、写分析报告、做调研
   > - **客户 / 案件 / 病人 / 候选人** —— 销售、律师、医生、HR、咨询
   > - **写文章 / 做内容** —— 自媒体、写作、课程、视频
   > - **流程 / SOP / 事故复盘** —— 运维、运营、质量
   > - **学习 / 笔记 / 复盘** —— 学生、自我成长

   据答**推荐主 + 辅工作模式 + domain**（映射见 `vault-format.md` 与 `docs/Obsidian-六大工作模式模板指南.md`），用一句话回确认（如「那默认走【项目交付 + 研究分析】、domain=product，行吗？」）。这步定提炼默认往哪个模式落，但**不预建空目录**。
4. **建骨架 + 记录路径**：按 `vault-format.md` 建——`00-Home.md` + 全部一级目录（`00-Inbox 10-Inputs 20-Process 30-Outputs 40-Feedback 50-MOCs 60-Domains 70-Assets 90-Archive _System/{Templates,Dashboards,Attachments}`）+ `50-MOCs/` 里 **6 张 MOC** + `.obsidian/app.json`（`{}`）+ 空骨架 `用户画像.md` / `CLAUDE.md`+`AGENTS.md`。**二级工作模式子目录、行业页都不预建（按需）**。**把 vault 绝对路径写进 `~/.second-brain-obsidian/vault_path`**（你直接写这个文本文件；之后读取 / 提炼都靠它，不再问）。
5. 接着做人格问答（§B）写画像。之后日常对话就靠 **§在场提炼** 每轮自检写库，无需任何安装。

> Obsidian 可选：vault 就是 markdown 文件夹，装了 Obsidian 能可视化浏览（https://obsidian.md），没装也照常读写。

## B. 采访 → 写画像（费曼「先把你是谁讲清」）

**B1 人格问答** —— 初始化时、或用户说「深度对我提问」：
- **① 先问要不要开语音**（**采访一开始就顺带问**，别等出完题用户才知道有语音）：「这轮采访想**开语音**吗？能像打电话一样逐题问你、更自然，但要配个 Azure 语音密钥（有免费额度）；**不开就走文字**，语音随时能加。」
  - 选语音 → 按 §语音 / §语音密钥 先把密钥配好（没配就用那段**明确引导话术**：① 听=Azure 必需 ② 读=MiniMax 可选，不配回退浏览器朗读）→ 起 `bridge.py` 语音页逐题问。没 Python → 说明语音要 Python、先走文字。
  - 选文字 / 没 Python → 文字（默认）。
- **② 出题（agent 自己出）**：覆盖 **6 个维度**——性格特质、价值观 / 做事原则、沟通 / 说话风格、思维 / 做事方式、行为处事 / 待人接物、偏好与禁忌（**维度规范名以 `vault-format.md` 为准**，写章节标题别改字）；每维 2-3 题、共约 15 题，口语化、具体、能引出真实回答（题库思路见 `SK/references/framework.md`，别照搬种子题）。
- **③ 答**：文字 → 题**一次性编号列出、让用户一条消息全填**，别逐题来回；语音 → 页面逐题朗读 + 听写。
- **④ 收尾**：把答案**当场提炼**成画像，按 `vault-format.md` 写进 `用户画像.md`（6 维 + 概览 + 变更日志）并同步重写 `CLAUDE.md` + `AGENTS.md`。

**B2 知识入库** —— 按 `vault-format.md` 的**自动判位**：先判知识层（Inputs=素材/来源、Process=思考/方法/在做的、Outputs=产出/决策/结论、Feedback=复盘/教训/洞察）→ 再判**工作模式**（研究分析/项目交付/客户个案/内容生产/流程运营/学习成长）→ 落 `<层一级目录>/<中文模式>/`（目录按需建）；判不出进 `00-Inbox/`。

## C. 分析会话（深度补充）

- **Claude Code（有 `/insights`）**：`/insights` 是内置斜杠命令（只能用户在输入框打，agent 调不了）。引导用户发 `/insights 分析我的会话`：命令生成报告落盘 `~/.claude/usage-data/report-*.html`，后半句触发本 skill 让你接管 → 你把报告 / insight 文本**直接提炼**成画像 deltas + 知识条目，按 `vault-format.md` 写进 vault（同 §在场提炼）。
- **Codex / Hermes（没有「分析会话内容」的 `/insights`；Hermes 的 `hermes insights` 只是用量统计）**：会话沉淀走**在场提炼**（§在场提炼，任何 agent 都行）——你在对话中发现用户新信息就直接写库；要回顾分析，让用户把要提炼的内容贴给你 / 指一个文件，你照样提炼入库。
> ❗ **不读 `~/.claude` / `~/.codex` 的原始 transcript**——只提炼用户给的内容 / `/insights` 产出。
> ⚠️ agent **运行不了** `/insights`（斜杠命令只有用户能触发）；别在代码里尝试调它。

## 知识库维护（按需）

都按四层归类、写成 `vault-format.md` 规定的笔记格式：
- **喂 URL**（用户说「收录这个链接 / 喂这个 URL」）：你用 **WebFetch** 抓 URL 正文 → 提炼 → 按自动判位写进 `<层>/<中文模式>/<YYYY-MM-DD> - <标题>.md`。
- **整理收件箱**（用户往 `<vault>/00-Inbox/` 丢了速记 `.md`、说「整理收件箱」）：你读 `00-Inbox/*.md` → 按自动判位写进 `<层>/<中文模式>/` → 把原速记移到 `00-Inbox/_archived/`。
- **体检知识库**（用户说「体检 / lint」）：你扫所有笔记，查**断链**（`[[X]]` 指向不存在的笔记）/ **孤儿**（无入链）/ **空笔记**，报告写 `<vault>/_体检.md`。
- **索引**：每次入库后更新 `00-Home.md`（总入口）+ 对应那张 `50-MOCs/MOC - <模式>.md`，格式见 `vault-format.md`。

## 在场提炼（每轮回复后 · 提示词驱动 · 唯一入库方式）

**这是日常入库的核心机制——不靠任何 hook / 后台进程，全靠你在对话里自己做：**

**每轮回复后，花一两秒过一遍这轮对话**：有没有得知用户的**新**画像特征 / 决策 / 观点 / 方法 / 知识 / 在做的项目 / 自己搭建·运营的系统工具（现有库没有、且有长期价值）？
- **有** → 立刻按 `SK/references/vault-format.md` 写进 vault：
  - 画像 → `用户画像.md` 对应维度（去重 + 记变更日志）；
  - 知识 → 按自动判位 `<层>/<中文模式>/<YYYY-MM-DD> - <标题>.md`（判层 + 模式、目录按需建、同标题合并、判不出进 `00-Inbox/`）；
  - 改完**同步重写** `CLAUDE.md` + `AGENTS.md`，并更新 `00-Home.md` + 对应 `50-MOCs/MOC - <模式>.md`。
- **没有**（纯闲聊 / 寒暄 / 搭建本系统的元对话）→ 跳过，别硬写。
- **任何话题都可能有料**（含项目、闲聊里关于用户的真实信息）——只要关于用户、有保留价值；唯一例外：明文密钥 / token 脱敏不写。
- 你本就有对话上下文，**直接提炼直接写**，别等用户开口；用户说「更新第二大脑」时一并补全。

> ⚠️ **没有后台自动提炼**（那要装 hook + Python，本版去掉了）——第二大脑能不能长起来，**全看你每轮有没有认真过这一遍**。别因为在忙主任务就跳过；这是唯一的入库方式。深度回顾走 `/insights`（§C）。

## 读取（注入画像）

- **vault 内·原生自动**：vault 根 `CLAUDE.md`（Claude Code）/ `AGENTS.md`（Codex、Hermes 都自动注入 `AGENTS.md`）（两份同内容、画像每次同步重写）——在 vault 目录开对应 agent **原生自动读**。这是默认读取方式。
- **任何项目里·手动**：用户说「加载第二大脑」→ 你读 `<vault>/用户画像.md` +（按需）`00-Home.md` / 相关 `10~40-*/<模式>/` 笔记，注入上下文「像用户一样」回答。

## 语音问答（打电话式 · 可选 · 唯一用 Python 处）

> **语音是本 skill 唯一用到 Python 的功能**（本地 Azure STT 桥）。没探测到 Python → 告诉用户「语音要 Python 环境，咱们先走文字问答」，其余功能照常。

用户选语音且有 Python 时：
1. `python3 SK/scripts/keys.py status` 看 `voice_ready`：已配 → 进第 2 步；**没配 → 别只甩「需要密钥」，按 §语音密钥 的话术明确引导用户（要什么 / 去哪拿 / 怎么发我），拿到就 `keys.py set` 存好；用户不想配 → 回退文字问答**。
2. 把这轮问题存 `/tmp/q.json`（`["问题1",...]`）。
3. `python3 SK/scripts/voice/bridge.py --questions /tmp/q.json --out /tmp/answers.json --background`
   —— **必须加 `--background`**（不加是前台 serve、会一直卡住你）。它**秒返回 URL**、自动开浏览器；
   把 URL 以**可点击 markdown 链接**发给用户（如 `[🎙️ 打开语音问答](http://127.0.0.1:8765/)`），
   说明会自动弹浏览器、没弹就点链接，然后点页面的「开始通话」。
4. 浏览器**像打电话**：MiniMax 音色自动朗读（页面右上角可选**男声 / 女声**，默认女声）→ 自动聆听 → 停顿即下一题；**同步显示文字 + 对话历史**。
5. **等用户说「答完了」**（或 `/tmp/answers.json` 写出后）→ 你读 `answers` **直接提炼写画像**（同 §B 收尾）。
   - `/tmp/answers.json` 带 **`reason`**：`completed`(答完) / `hangup`(主动结束) → 正常入库；
     **`error` / `closed`（异常 / 中途关页面）→ 告诉用户「语音异常结束」，问要不要重试或转文字**，别当成功。

## 语音密钥（随时设置 · 需 Python）

- `python3 SK/scripts/keys.py status` 看现状；`keys.py set --azure-key <KEY> [--azure-region koreacentral] [--minimax-key <KEY>]`。
- 必需 Azure STT；可选 MiniMax（更自然音色，不填用浏览器 TTS）。密钥仅存 `~/.second-brain-obsidian/secrets.env`（chmod 600）。
- **没配时这样引导用户**（讲清要什么 / 去哪拿 / 怎么给，别只说「需要密钥」；**「听」和「读」分开说**）：
  > 语音作答要两块密钥，作用不同：
  > ① **听你说话（必需）= 微软 Azure 语音**：去 `portal.azure.com` 建个「Speech / 语音服务」资源 → 拿 **Key** + **Region**（如 `koreacentral`）。有免费额度，够用。
  > ② **朗读问题（可选）= MiniMax 音色**：配了朗读更自然、可男 / 女声；**不配也能用**——回退浏览器自带朗读（免费、能用，只是没那么自然）。想要就再给我一个 **MiniMax** key。
  > 把密钥发我，我帮你存进本机 `secrets.env`（只存本地、不外传 / 不进 git）。或者**先走文字问答**，语音随时能加。

  拿到后跑 `keys.py set --azure-key <KEY> --azure-region <REGION> [--minimax-key <KEY>]` 存好，再起语音页。

---

## 文件

- **语音问答（可选 · 用 Python）**：`scripts/voice/bridge.py` + `scripts/voice/web/index.html`（打电话式 STT + 对话历史）、`scripts/keys.py`（语音密钥，存 `~/.second-brain-obsidian/secrets.env`，chmod 600）、`scripts/store.py`（语音小工具 / 密钥路径 / 原子写）。
- 建库 / 采访 / 读取 / 在场提炼 / 知识维护**全是 agent 直接读写 vault markdown**（按 `references/vault-format.md`）——**不用 Python、不装 hook、无后台进程**。

## 注意

- **提示词驱动 · 零依赖**：建库 / 采访 / 读取 / 提炼 / 知识维护全由 agent 在对话里直接读写 vault markdown 完成；**不装 hook、不跑后台进程**。仅可选语音问答用 Python。
- **初始化主动发起，之后每轮在场提炼**：采访按需触发；日常**每轮回复后**自检 + 写库（§在场提炼）。深度补充走 `/insights`。
- **知识结构**：四层（Inputs/Process/Outputs/Feedback）一级目录 + 六大工作模式按需中文子目录 + 行业映射页；入库按 `vault-format.md` 自动判位（先层 → 再模式 → 判不出进 00-Inbox）。
- **隐私**：全程本地；语音密钥仅在 `secrets.env`，绝不进 vault/git；提炼时对密钥/token 脱敏（别写进库）。
- **统一一份**：所有 agent 共享同一 vault 的同一份画像 + 知识。
- **跨平台（mac / Windows）**：默认库位置 mac=iCloud Obsidian 目录、Win=`~/Documents`；语音命令里 `python3` 在 Win 用 `python` / `py`。
