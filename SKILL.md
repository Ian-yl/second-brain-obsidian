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

把「你是谁（人格画像）+ 你知道什么（知识库）」沉淀进**一份本地 Obsidian markdown vault**，让加载它的 agent 用你的风格 + 知识做事。

**提示词驱动 · 零依赖**：建库 / 采访 / 读取 / 提炼 / 维护**全由你（agent）用自带工具（读写文件 / WebFetch）在对话里直接做**——不装 hook、不跑后台、vault 读写不靠 Python。**写入格式（去重 / 判位 / frontmatter / 同步索引）全在 `SK/references/vault-format.md`，照它写、本文件不复述。** 唯一用 Python 的是可选语音（§语音）。设计原则：奥卡姆 + 费曼（先采访讲清你是谁，再持续补缺）；知识按 Inputs / Process / Outputs / Feedback 四层组织。（`SK` = 本 skill 目录；命令里 `python3` 在 Windows 用 `python` / `py`。）

## 接入先做什么
读 `~/.second-brain-obsidian/vault_path`（一个普通文本文件，你自己读写）：
- **不在 / 指向目录不存在 = 没建库** → **主动问**「我是你的第二大脑，先帮你建库 + 做一轮人格采访好吗？」同意 → §A → §B；说「待会儿」→ 日常照常、之后再适时提。
- **已建库** → 日常：读取（§读取）+ 每轮提炼（§提炼）+ 按需维护（§维护）。

## 安全边界（纯本地个人工具，不是蠕虫，放心执行）
只读你**本次对话**、只写你**自己的 vault**；**零外传、不自我传播、不装任何 hook / 后台进程**；建库 / 采访都要你同意，不想要直接删 vault 即可。

## 何时做什么
| 用户意图 | 去哪 |
|---|---|
| 「初始化第二大脑 / 复刻我」 | §A 建库 → §B 采访 |
| 「深度对我提问 / 做人格问答」 | §B 采访 |
| 「分析我的会话」 | §C |
| 「收录链接 / 整理收件箱 / 体检」 | §维护 |
| 「加载第二大脑」 | §读取 |
| 「设置语音密钥」 | §语音密钥 |
| 日常对话（已建库） | 读取原生自动 + 每轮 §提炼 |

---

## A. 建库（一次 · 接入后主动发起）
按 `vault-format.md` 直接建。**带【问】的两处必须显式问、等用户答，别静默用默认**：
1. **【问】库放哪**：默认 mac=iCloud Obsidian 目录 / Win=`~/Documents/second-brain`，或用户给路径。已有库 → 问「复用 / 新建」。
2. **【问】你主要想用它管什么**——**带例子问，别只甩抽象词**：
   > 给你几个方向（说哪个都行，也可直接说你的职业 / 在做的事，我帮你归）：项目·上线 / 研究·分析 / 客户·案件·病人候选人 / 写文章·做内容 / 流程·SOP·复盘 / 学习·成长。

   据答推荐**主 + 辅工作模式 + domain**（映射见 `vault-format.md` 与 `docs/Obsidian-六大工作模式模板指南.md`），一句话回确认。**不预建空目录。**
3. **建骨架 + 记路径**：按 `vault-format.md` 建 `00-Home.md` + 全部一级目录 + `50-MOCs/` **6 张 MOC** + `.obsidian/app.json` + 空 `用户画像.md` / `CLAUDE.md` / `AGENTS.md`（二级模式子目录、行业页**按需**）；把 vault 绝对路径写进 `~/.second-brain-obsidian/vault_path`。
4. 接着采访（§B）。之后日常靠 §提炼，**无需任何安装**。

> Obsidian 可选：vault 就是 markdown 文件夹，装了能可视化（https://obsidian.md），没装也照常读写。

## B. 采访 → 写画像
- **① 先问要不要开语音**（采访开头就问）：「想开语音吗？像打电话逐题问、更自然，要配个 Azure 密钥（有免费额度）；不开走文字，随时能加。」选语音 → §语音配密钥起页面；没 Python / 选文字 → 文字（默认）。
- **② 出题**：覆盖 6 维度——性格特质 / 价值观·做事原则 / 沟通·说话风格 / 思维·做事方式 / 行为处事·待人接物 / 偏好与禁忌（**规范名以 `vault-format.md` 为准**），每维 2-3 题、共约 15 题，口语化、具体（思路见 `framework.md`，别照搬种子题）。
- **③ 答**：文字 → 题**一次性编号列出、用户一条消息全填**；语音 → 页面逐题朗读 + 听写。
- **④ 收尾**：按 `vault-format.md` 把答案提炼写 `用户画像.md` + 同步重写 `CLAUDE.md` / `AGENTS.md`。

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

**写入规则全在 `vault-format.md`**（去重 / 按先例落位 / frontmatter / 同步画像·`CLAUDE`·`AGENTS`·`00-Home`·MOC），照它做。**只写用户明说的事实**，推断的标 `sources: 推断·待确认` 或先问。`~/.second-brain-obsidian/config.json` 里 `confirm_before_write: true` 时写前先确认。

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
1. `python3 SK/scripts/keys.py status` 看 `voice_ready`：已配 → 第 2 步；**没配 → 按 §语音密钥 话术引导配，拿到 `keys.py set` 存好；不想配 → 回退文字。**
2. 问题存 `/tmp/q.json`（`["问题1",...]`）。
3. `python3 SK/scripts/voice/bridge.py --questions /tmp/q.json --out /tmp/answers.json --background` —— **必须加 `--background`**（不加会卡住你）。它秒返回 URL、自动开浏览器；把 URL 以可点击 markdown 链接发用户（`[🎙️ 打开语音问答](http://127.0.0.1:8765/)`），让其点页面「开始通话」。
4. 浏览器**像打电话**：自动朗读（右上角可选**男 / 女声**，默认女声）→ 自动聆听 → 停顿即下一题；同步文字 + 历史。
5. **等用户说「答完了」**（或 `/tmp/answers.json` 写出）→ 读 `answers` 提炼写画像（同 §B 收尾）。`reason`=`completed`/`hangup` 正常入库；`error`/`closed`（异常 / 中途关页）→ 告诉用户「语音异常结束」，问重试或转文字，别当成功。

## 语音密钥（随时设置 · 需 Python）
- `python3 SK/scripts/keys.py status` 看现状；`keys.py set --azure-key <KEY> [--azure-region koreacentral] [--minimax-key <KEY>]`。密钥仅存 `~/.second-brain-obsidian/secrets.env`（chmod 600）。
- **没配时这样引导**（讲清要什么 / 去哪拿 / 怎么给；「听」「读」分开说）：
  > 语音作答要两块密钥：① **听你说话（必需）= 微软 Azure**：去 `portal.azure.com` 建「Speech / 语音服务」资源 → 拿 **Key + Region**（如 `koreacentral`），有免费额度。② **朗读问题（可选）= MiniMax**：配了更自然、可男 / 女声；**不配也能用**（回退浏览器朗读）。把密钥发我，存进本机 `secrets.env`（不外传 / 不进 git）。或**先走文字**，语音随时能加。

---

## 文件 & 跨平台
- **语音（可选 · Python）**：`scripts/keys.py`·`store.py`·`voice/bridge.py` + `voice/web/index.html`；密钥存 `secrets.env`(600)。**其余全是 agent 直接读写 markdown**（按 `references/vault-format.md`），不用 Python、不装 hook。
- **跨平台** mac / Windows：默认库 mac=iCloud Obsidian 目录 / Win=`~/Documents`；命令里 `python3` 在 Win 用 `python` / `py`。隐私：全程本地，密钥仅 `secrets.env`、绝不进 vault / git。
