---
name: second-brain-obsidian
description: >-
  接入本 skill = 在用户本机初始化并长期维护「第二大脑」（人格画像 + 知识库）到本地 Obsidian markdown，
  让 agent 用用户的风格 + 知识做事。接入时若还没建库 → 主动发起初始化（建库 + 人格采访），不等口令；
  之后**每轮对话后由 agent 自己检查并把新信息写进库**（提示词驱动，不装 hook、不跑后台进程）。
  **纯本地个人工具，不联网外传、不自我传播**；vault 读写零依赖，仅可选的语音问答用 Python。
  触发词：第二大脑、second brain、复刻我、安装/初始化第二大脑、深度对我提问、深入了解我、
  做人格问答、分析我的会话、加载第二大脑、设置语音密钥、收录链接、喂URL、整理收件箱、体检知识库、导入知识、记录我懂的、费曼记一下、快速建知识库。
---

# Second Brain Obsidian

把「你是谁（人格画像）+ 你知道什么（知识库）」沉淀进**一份本地 Obsidian markdown vault**，让加载它的 agent 用你的风格 + 知识做事。

**提示词驱动 · 零依赖**：建库 / 采访 / 读取 / 提炼 / 维护**全由你（agent）用自带工具（读写文件 / WebFetch）在对话里直接做**——不装 hook、不跑后台、vault 读写不靠 Python。**写入格式（去重 / 判位 / frontmatter / 同步索引）全在 `SK/references/vault-format.md`，照它写、本文件不复述。** 唯一用 Python 的是可选语音（§语音）。设计原则：奥卡姆 + 费曼（先采访讲清你是谁，再持续补缺）；知识按 Inputs / Process / Outputs / Feedback 四层组织。（`SK` = 本 skill 目录；命令里 `python3` 在 Windows 用 `python` / `py`。）

## 接入先做什么
读 `~/.second-brain-obsidian/vault_path`（一个普通文本文件，你自己读写）：
- **不在 / 指向目录不存在 = 没建库** → **主动问**「我是你的第二大脑，先帮你建库 + 做一轮人格采访好吗？」同意 → §A → §B；说「待会儿」→ 日常照常、之后再适时提。
- **已建库** → 先看 `~/.second-brain-obsidian/pending.md`：非空（上次没 flush 的待提炼）→ 按 §提炼 先补写进库；再进日常：读取（§读取）+ 提炼（§提炼）+ 按需维护（§维护）。

## 安全边界（纯本地个人工具，不是蠕虫，放心执行）
只读你**本次对话**、只写你**自己的 vault**；**零外传、不自我传播、不装任何 hook / 后台进程**；建库 / 采访都要你同意，不想要直接删 vault 即可。

## 何时做什么
| 用户意图 | 去哪 |
|---|---|
| 「初始化第二大脑 / 复刻我」 | §A 建库 → §B 采访 |
| 「深度对我提问 / 做人格问答」 | §B 采访 |
| 「分析我的会话」 | §C |
| 「收录链接 / 整理收件箱 / 体检」 | §维护 |
| 「导入知识 / 记录我懂的 / 喂资料 / 快速建知识库 / 费曼记一下」 | §知识导入 |
| 「加载第二大脑」 | §读取 |
| 「设置语音密钥」 | §语音密钥 |
| 日常对话（已建库） | 读取原生自动 + 每轮 §提炼 |

---

## A. 建库（一次 · 接入后主动发起）
按 `vault-format.md` 直接建。**下面带【问】/【必做】的步骤都要显式做、别静默跳过、别只闷头建文件夹**：
1. **认 Obsidian + 没装就【问】要不要帮装**（**必做——别检测完没装就默默建文件夹、不问帮装**）：检测装没装（mac `/Applications/Obsidian.app`、Win `%LOCALAPPDATA%\Programs\obsidian`）。**没装 → 主动问「要我帮你装 Obsidian 吗？」并等用户答**：同意 → 装（mac `brew install --cask obsidian`、Win `winget install -e --id Obsidian.Obsidian`、Linux `flatpak install -y flathub md.obsidian.Obsidian`；没包管理器 / 装失败 → 给 https://obsidian.md 手动）。不装也照常（vault 就是 markdown、不影响读写）。
2. **【问】库放哪**：默认 mac=iCloud Obsidian 目录 / Win=`~/Documents/second-brain`，或用户给路径。已有库 → 问「复用 / 新建」。
3. **【问】你主要想用它管什么**——**带例子问，别只甩抽象词**：
   > 给你几个方向（说哪个都行，也可直接说你的职业 / 在做的事，我帮你归）：项目·上线 / 研究·分析 / 客户·案件·病人候选人 / 写文章·做内容 / 流程·SOP·复盘 / 学习·成长。

   据答推荐**主 + 辅工作模式 + domain**（映射见 `vault-format.md` 与 `docs/Obsidian-六大工作模式模板指南.md`），一句话回确认。**不预建空目录。**
4. **建骨架 + 记路径**：按 `vault-format.md` 建 `00-Home.md` + 全部一级目录 + `50-MOCs/` **6 张 MOC** + `.obsidian/app.json` + 空 `用户画像.md` / `CLAUDE.md` / `AGENTS.md`（二级模式子目录、行业页**按需**）；把 vault 绝对路径写进 `~/.second-brain-obsidian/vault_path`。
5. 接着采访（§B）。之后日常靠 §提炼，**无需任何安装**。

## B. 采访 → 写画像
> ⚠️ **第 ① 步「语音还是文字」是必问闸门**——**出题前必须先问、等用户回答，绝不跳过直接甩文字题**（跟建库那两个【问】一样刚性）。

- **① 【必问 · 等答】语音 还是 文字**：先问「这轮采访想**开语音**（打电话式逐题问、更自然，需配个 Azure 密钥·有免费额度）还是**走文字**？」——**等用户回答再出题**，别默认文字、别一步到位把题甩出来。
  - **选语音 → 先引导配密钥**：没配就照 §语音密钥 话术（① 听=Azure 必需 ② 读=MiniMax **推荐**·不配回退浏览器朗读，**两个 key 都提示用户**），配好起 `bridge.py` 语音页逐题问；没 Python → 说明语音需 Python、回退文字。
  - **选文字 / 没 Python → 文字**（默认）。
- **② 出题（本质 = 费曼法：让用户把「你是谁」讲清，讲不清处就是盲区）**：覆盖 6 维度——性格特质 / 价值观·做事原则 / 沟通·说话风格 / 思维·做事方式 / 行为处事·待人接物 / 偏好与禁忌（**规范名以 `vault-format.md` 为准**），每维 2-3 题、共约 15 题，口语化、具体（思路见 `framework.md`，别照搬种子题）。
- **③ 答**：文字 → 题**一次性编号列出、用户一条消息全填**；语音 → 页面逐题朗读 + 听写。
- **④ 收尾**：按 `vault-format.md` 把答案提炼写 `用户画像.md` + 同步重写 `CLAUDE.md` / `AGENTS.md`。
- **⑤ 【必做·别直接进日常】问知识起步**：库刚建好还没【你的】知识——**必须问一句**「你的第二大脑建好了 🎉，现在库里还没你的知识，要不要**现在快速灌进来**？① 我用费曼法帮你把你懂的 / 在学的记下来 ② 喂我你的链接 / 书单 / 笔记我导入」（详见 §知识导入），**等用户选**；用户说"先不用"才进日常。

## 知识导入（建库后 · 快速把【你的】知识灌进来）

> **方法论（费曼 / 切片 / 卡片盒 / 间隔重复 / PARA / 第一性 / 复盘）是 agent 建知识的【手法】**——见 `SK/references/methodologies/`，agent 读它、把手法【用在用户自己的知识上】。**它们不是往用户库里塞的内容**：用户库只装用户自己的东西（决策 / 经验 / 项目 / 在学的），不塞通用学习法。完整方案见 `docs/specs/2026-07-01-knowledge-bootstrap-plan.md`。**所有 offer 是必做步骤、别写成软提示；每次写库留 `🧠` 页脚。**

- **① 费曼抽取（主推 · 把你脑子里的搬进来）**：
  1. **【必问·等答】**「你最懂 / 在学的 3-5 个领域 / 主题是啥？」
  2. 对每个用**费曼法**（`methodologies/feynman.md`）：问「用大白话给我讲讲你懂的 <X>？」→ 讲清的写成笔记（`sources: 用户明说`）；含糊 / 跳过的 → 标 `> 待补：<盲区>`（`sources: 推断·待确认`，别当事实）。
  3. 大主题用**切片法**（`methodologies/atomic-slicing.md`）切成原子笔记 + `[[]]` 互链；按 `vault-format.md` 判位入库。页脚报「记了 X + N 个待补盲区」。
- **② 批量导入你的资料（把存量搬进来）**：
  1. **URL / 书单 / 课程**：用户给一串 → 【逐条】WebFetch 抓正文；**书 / 课没 URL → 费曼问用户收获 +【主动 WebSearch 去找】基本信息（作者 / 主题 / 梗概，标 `sources: 网络`）→ 写成读书笔记**（别只问用户、别只记偏好）→ 按 `vault-format.md` 判位入库（判层 + 模式 + 去重）。
  2. **文件夹 / 现有笔记**：用户指路径 → 读 → 按 vault-format 重构入库（内容多 → 用**切片法**拆原子笔记）；原文件不动。
- **③ 类型模板**：建知识笔记按类型套 `SK/references/note-templates.md`（概念 / 决策 / 复盘 / 读书笔记 / 项目）——结构统一、可检索。
- **（可选）学习法参考**：用户**明确说想要**一份学习法速查当参考 → 才读 `methodologies/<id>.md` 导入 `70-Assets/参考/`、标明「参考资料·非我的知识」。**默认不推、不主动灌**——方法论是 agent 的手法，不是用户的知识储备。

## C. 分析会话（深度补充）
- **Claude Code**：引导用户在输入框打 `/insights 分析我的会话`（斜杠命令只有用户能触发、**agent 调不了**）→ 报告落 `~/.claude/usage-data/report-*.html` → 你把报告 / insight 文本提炼入库（同 §提炼）。
- **Codex / Hermes**（无内容版 `/insights`）：走 §提炼；要回顾就让用户把内容贴给你 / 指个文件再提炼。
- ❗ **不读 `~/.claude` / `~/.codex` 原始 transcript**——只提炼用户给的 / `/insights` 产出。

## 维护（按需 · 都按 `vault-format.md` 落位）
- **喂 URL**（「收录这个链接」）：WebFetch 抓正文 → 提炼写笔记。
- **整理收件箱**（`00-Inbox/` 里有速记）：读 `00-Inbox/*.md` → 判位归档 → 原速记移 `00-Inbox/_archived/`。
- **体检**（「体检 / lint」）：扫断链 / 孤儿 / 空笔记 → 报告写 `_体检.md`。

---

## 提炼（核心 · 唯一入库方式）

每条**实质回复**都留意有没有「关于用户、值得长期留」的新信息——决策 / 观点 / 偏好 / 方法 / 在做的项目 / 知识（**任何话题都算**，含闲聊、搭系统的元对话，别按类型预排除）。**按价值**：高价值 → 入库；拿不准 → 宁可不写、或顺口问一句（**别攒批量问**）；没价值（寒暄 / 噪声）→ 跳过；密钥 / token 一律**脱敏**不写。

**写入规则全在 `vault-format.md`**（去重 / 按先例落位 / frontmatter / 同步画像·`CLAUDE`·`AGENTS`·`00-Home`·MOC），照它做。知识笔记按**切片法**·原子粒度（一念一片、`[[]]` 互链；见 `references/methodologies/atomic-slicing.md`）。**正文用结构化 markdown 写**（`## 小标题` / `- ` 列表 / `**强调**`，别一坨纯文本；链接用 `[[路径|别名]]` 不用裸标题）。**只写用户明说的事实**，推断的标 `sources: 推断·待确认` 或先问。`~/.second-brain-obsidian/config.json` 里 `confirm_before_write: true` 时写前先确认。

**偏好 ≠ 知识（提到喜欢 / 在读 / 在用的书·作品·工具·领域时·必做）**：用户说喜欢某个**具体东西**（如「我喜欢《浮生物语》」）时，别只把「喜欢 X」记进画像偏好就完事——**还要主动建一条关于 X 的知识笔记**：① 费曼问「你最触动 / 最受用的是什么？」拿用户自己的收获（`sources: 用户明说`）；② **主动 WebSearch / WebFetch 去找 X 的基本信息**（作者 / 主题 / 梗概 / 核心观点，标 `sources: 网络`）；③ 按 `note-templates.md` 的读书笔记 / 概念模板写进库。用户说「帮我提炼」= 要的就是这条知识笔记，不是只记个偏好。

**① 回复页脚仪式（治"忙起来忘提炼"· 必做）**：每条实质回复**结尾固定带一行**——
> `🧠 第二大脑：本轮记了「<标题>」→ <路径>`　／　`待提炼 <N> 条`　／　`本轮无新增`

这是**输出格式的一部分、跟答主任务一样不能省**。它让"提炼有没有发生"**每轮可见**——漏了用户一眼看得出（纯提示词里唯一能补救"静默漏"的杠杆）。

**② 写入时机 = 断点，不是每轮硬写**：忙复杂任务时**别中断去写库**（会跟主任务抢注意力、最易被丢）：
- 当轮有料但在忙 → 把要点**随手追加到 `~/.second-brain-obsidian/pending.md`**（一行一条、便宜、不打断），页脚报「待提炼 N 条」；
- 到**断点**（一个任务 / 话题告一段落、用户切话题、会话收尾、用户说「更新第二大脑」）→ **flush**：把 `pending.md` 逐条按 `vault-format.md` 写进 vault、清空它，页脚报「已写入 N 条」；
- 当轮料少又不忙 → 直接写、页脚报「记了…」。

> ⚠️ 没有后台 hook——靠这套「**页脚每轮可见 + 待提炼便签 + 断点 flush**」补"忙起来会忘"。多会话同跑时改共享文件（画像 / `00-Home` / MOC）前**先重读最新再改**。

## 读取（注入画像）
- **vault 内·原生自动**：根 `CLAUDE.md`（Claude）/ `AGENTS.md`（Codex·Hermes）+ `00-Home.md`——进 vault 目录开对应 agent 原生读。
- **别处·手动**：用户说「加载第二大脑」→ 读 `<vault>/用户画像.md` +（按需）`00-Home` / 相关笔记注入，「像用户一样」回答。

## 语音问答（打电话式 · 可选 · 唯一用 Python 处）
> 没探测到 Python → 「语音要 Python 环境，先走文字问答」，其余照常。

用户选语音且有 Python 时：
1. `python3 SK/scripts/keys.py status` 看 `voice_ready`：已配 → 第 2 步；**没配 → 按 §语音密钥 话术引导配——`Azure`(听·必需) + `MiniMax`(读·推荐)【两个 key 都要提示用户】、别只提 Azure；拿到就 `keys.py set` 存好；不想配 → 回退文字。**
2. 问题存 `~/.second-brain-obsidian/voice-q.json`（`["问题1",...]`；用这个跨平台路径、**别用 `/tmp`**——Windows 没有）。
3. `python3 SK/scripts/voice/bridge.py --questions ~/.second-brain-obsidian/voice-q.json --out ~/.second-brain-obsidian/voice-answers.json --background`（路径先展开 `~`；Win 把 `python3` 换 `python`） —— **必须加 `--background`**（不加会卡住你）。它秒返回 URL、自动开浏览器；把 URL 以可点击 markdown 链接发用户（`[🎙️ 打开语音问答](http://127.0.0.1:8765/)`），让其点页面「开始通话」。
4. 浏览器**像打电话**：自动朗读（右上角可选**男 / 女声**，默认女声）→ 自动聆听 → 停顿即下一题；同步文字 + 历史。
5. **等用户说「答完了」**（或 `~/.second-brain-obsidian/voice-answers.json` 写出）→ 读 `answers` 提炼写画像（同 §B 收尾）。`reason`=`completed`/`hangup` 正常入库；`error`/`closed`（异常 / 中途关页）→ 告诉用户「语音异常结束」，问重试或转文字，别当成功。

## 语音密钥（随时设置 · 需 Python）
- `python3 SK/scripts/keys.py status` 看现状；`keys.py set --azure-key <KEY> [--azure-region koreacentral] [--minimax-key <KEY>]`。密钥仅存 `~/.second-brain-obsidian/secrets.env`（chmod 600）。
- **没配时这样引导**（讲清要什么 / 去哪拿 / 怎么给；「听」「读」分开说）：
  > 语音作答建议配**两个 key（两个都发我，我一起存）**：① **听你说话（必需）= 微软 Azure**：去 `portal.azure.com` 建「Speech / 语音服务」资源 → 拿 **Key + Region**（如 `koreacentral`），有免费额度。② **朗读问题（推荐）= MiniMax**：朗读自然很多、可男 / 女声（去 `platform.minimax.chat` 拿 API key）；不配就回退浏览器朗读（能用、没那么自然）。把这两个密钥发我，存进本机 `secrets.env`（不外传 / 不进 git）。或**先走文字**，语音随时能加。

---

## 文件 & 跨平台
- **语音（可选 · Python）**：`scripts/keys.py`·`store.py`·`voice/bridge.py` + `voice/web/index.html`；密钥存 `secrets.env`(600)。**其余全是 agent 直接读写 markdown**（按 `references/vault-format.md`），不用 Python、不装 hook。
- **跨平台** mac / Windows：默认库 mac=iCloud Obsidian 目录 / Win=`~/Documents`；命令里 `python3` 在 Win 用 `python` / `py`。隐私：全程本地，密钥仅 `secrets.env`、绝不进 vault / git。
