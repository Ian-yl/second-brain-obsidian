# Second Brain Obsidian — 设计文档

- 日期：2026-06-27 ｜ 状态：已实现
- skill 名：`second-brain-obsidian`

---

## 1. 概述与定位

把「**你是谁**（人格画像）+ **你知道什么**（知识库）」沉淀进 Obsidian 的**统一一份** vault，
让加载它的 agent「用你的风格 + 调你的知识」做事 ≈ 复刻你。

- **统一一份**：一份画像 + 一套知识，各 agent（Claude Code / Codex / Hermes）共享同一 vault。
- **agent-native**：建库 / 采访 / 读取 / 更新 / 知识维护由 **agent 直接读写 vault markdown** 完成（这部分不靠 Python）；但**自动提炼（默认开）和语音需要 Python**（安装时自动备好）。写入格式见 `references/vault-format.md`。
- **接入即初始化**：接入本 skill 且检测到没建库 → **主动发起**建库 + 采访（不等用户喊口令）；之后日常对话自动提炼。
- **纯本地·非蠕虫**：只读用户自己刚结束的对话、只写用户自己的 Obsidian，零外传、不自我传播、可一键 `--remove` 关；SKILL.md/脚本里都显式声明，避免被误判为蠕虫。
- **设计原则**：奥卡姆（能简则简、手动低频）+ 费曼（先采访讲清「你是谁」，再分析补缺）。

## 2. 架构

全程 agent 用自带工具（读写文件 / WebFetch）直接维护 vault（vault 读写本身是纯 markdown、不靠 Python）；但**需要 Python——本地自动提炼（默认开）+ 语音问答（可选）都靠它；安装时自动检测并按需装好（检测 → 装 → 验证 → 不行重装），用户无需手配**。

```
second-brain-obsidian/
├── SKILL.md                       # agent 编排：建库 / 采访 / 读取 / 更新 / 知识维护的指令
├── references/
│   ├── vault-format.md            # vault 写入规范（画像/知识/00-Home/MOC/CLAUDE+AGENTS 格式 + 去重 + 四层一级目录×六大工作模式自动判位）
│   ├── framework.md               # 人格问答的 6 维度框架 + 种子问题
│   └── setup.md                   # 安装与配置
├── agents/openai.yaml             # Codex 清单
└── scripts/                       # 需 Python：本地自动提炼(默认开) + 语音问答(可选)
    ├── voice/bridge.py + web/index.html   # 打电话式语音问答（Azure STT + MiniMax TTS + 对话历史）
    ├── keys.py                    # 语音密钥读写（secrets.env，chmod 600）
    ├── store.py                   # 语音小工具（密钥路径 / 原子写 / 跨平台后台派生）
    ├── install.py                 # 注册本地 hook（SessionEnd 或 Stop）+ 记 vault 路径（默认开·本地自动提炼）
    └── hook_entry.py              # 后台提炼写 vault（引擎=当前会话 agent claude/codex/hermes；纯本地、不外传）

<vault>/                           # agent 建/复用；mac=iCloud Obsidian 目录、Windows=~/Documents
├── 00-Home.md  用户画像.md  CLAUDE.md  AGENTS.md  .obsidian/
├── 00-Inbox/  10-Inputs/ 20-Process/ 30-Outputs/ 40-Feedback/   # 四层一级目录；下按需建 6 个中文工作模式子目录
└── 50-MOCs/（6 张模式 MOC）  60-Domains/（行业页·按需）  70-Assets/  90-Archive/  _System/

~/.second-brain-obsidian/secrets.env(600)   # 仅语音密钥
```

## 3. 数据模型（vault；完整格式见 `references/vault-format.md`）

### 3.1 人格画像 `用户画像.md`
frontmatter（`type/updated/framework_version/tags`）+ 固定 8 段：概览 + 6 维度（性格特质、价值观 / 做事原则、沟通 / 说话风格、思维 / 做事方式、行为处事 / 待人接物、偏好与禁忌）+ 变更日志。
- 每维度 0+ 条 `- ` 要点；加要点先语义去重；变更日志保留最近 50 条；`tags` 并入 frontmatter。

### 3.2 知识 `<层一级目录>/<中文工作模式>/<YYYY-MM-DD> - <标题>.md`
四层（Inputs/Process/Outputs/Feedback）一级目录 × 六大中文工作模式按需子目录。frontmatter（`type/layer/mode/domain/created/updated/aliases/tags/sources`）+ `# 标题` + 正文。
- **自动判位**：先判知识层 → 再按「对象+动作+产出」判工作模式 → 落对应目录（不存在自动建）；判不出进 `00-Inbox/`。同标题合并、不堆叠重复段落。

### 3.3 索引 `00-Home.md` + `50-MOCs/MOC - <模式>.md` + `CLAUDE.md` / `AGENTS.md`
`00-Home.md`（总入口）：从这开始 / 六大模式 MOC 入口 / 常用领域 / 最近输出·复盘（dataview）。`50-MOCs/` 六张模式 MOC（建库就建）。`CLAUDE.md` / `AGENTS.md`（vault 根·两份同内容）= 画像摘要，Claude 读前者、Codex/Hermes 读后者，默认读取注入。

## 4. 核心流程（全 agent-native）

### 4.1 建库（一次）
接入本 skill 检测无库即主动发起。**显式问且等答**：① 库放哪 ② 主要管什么（**带例子**→推荐主+辅模式+domain）。按 `vault-format.md` 建骨架：`00-Home.md` + 全部一级目录 + `50-MOCs/` 六张 MOC + `.obsidian/app.json` + 空 `用户画像/CLAUDE/AGENTS`；二级模式目录、行业页按需建。

### 4.2 采访（人格问答）
agent 自己出题，覆盖 6 维度、共约 15 题（框架见 `framework.md`）。用户文字一次性填，或实时语音作答（§5）。agent 把答案提炼成画像，写进 `用户画像.md` + 同步 `CLAUDE.md`/`AGENTS.md`。

### 4.3 更新（自动提炼默认开 + 在场提炼）
对话中得知用户**新**画像/知识（库里没有、有长期价值）时，agent 主动提炼，按 `vault-format.md` 写进 vault：画像归维度（去重 + 变更日志），知识按**自动判位**落 `<层>/<中文模式>/`（同标题合并、判不出进 00-Inbox），同步 `CLAUDE.md`/`AGENTS.md` + 更新 `00-Home.md`/对应 MOC。
**默认开·本地自动（两模式，初始化时让用户选）**：跑 `install.py --mode end|stop`——`end`=SessionEnd 读整段一次提炼（省）；`stop`=Stop 每条回复后增量提炼（进度标记防重复，实时/更稳）。后台起提炼引擎（`claude -p`/`codex exec`/`hermes -z`，默认用当前会话的 agent（注册时标记），可用 `engine` 文件强制；claude/codex 带 `--strict-mcp-config` 不加载 MCP）读对话、按 vault-format 提炼写 vault；**任何话题都收**（含搭建本系统、项目、闲聊），仅明文密钥/token 脱敏。**纯本地、零外传**；需要 Python + `claude`/`codex`/`hermes` 任一 CLI（§0 自动备齐）。Hermes 的 hook 在 `~/.hermes/config.yaml`（end→`on_session_finalize` 整会话一次 / stop→`on_session_end` 每回合——注意 Hermes 命名反直觉：`on_session_end` 其实是**每回合**触发；payload 仅 session_id → 用 `hermes sessions export` 取对话、摊成每条一行增量；首次需 `hermes --accept-hooks` 同意）。**Hermes 会重写 config.yaml 抹掉注释**，故 `install.py` 靠**命令特征**（含 `hook_entry.py`）定位本 skill 的 hook 来增删、不依赖哨兵注释（`_strip_our_hermes_hook`，仅当 hooks: 含非本 skill 的 hook 才交还手动）；切模式 / 重写后 allowlist 失效，需重新 `--accept-hooks`。

### 4.4 分析会话（深度补充）
- **Claude Code**：用户在输入框打 `/insights 分析我的会话`（斜杠命令只有用户能触发）→ 报告落盘 `~/.claude/usage-data/report-*.html` → agent 把报告文本直接提炼入库。
- **Codex / Hermes（无「分析会话内容」的 `/insights`；`hermes insights` 只是用量统计）**：会话沉淀走在场提炼（§4.3，任何 agent 都行）；要回顾分析，用户把要提炼的内容贴给 agent / 指一个文件，agent 提炼入库。
- 不读原始 transcript，只提炼用户给的内容 / `/insights` 产出。

### 4.5 知识库维护
- 喂 URL：agent 用 WebFetch 抓正文 → 提炼 → 写对应层笔记。
- 整理收件箱：读 `00-Inbox/*.md` → 按自动判位写进 `<层>/<中文模式>/` → 原速记移到 `00-Inbox/_archived/`。
- 体检：扫所有笔记查断链 / 孤儿 / 空笔记 → 报告写 `_体检.md`。

### 4.6 读取
vault 内原生自动读 `CLAUDE.md`（Claude Code）/ `AGENTS.md`（Codex、Hermes）+ `00-Home.md` 总入口；任何项目里用户说「加载第二大脑」→ agent 读 `用户画像.md` + 相关笔记注入上下文。

## 5. 实时语音问答（可选·用 Python）

- 栈：**STT = 微软 Azure Speech**（短期 token，浏览器端 SDK 实时识别 zh-CN）；**TTS = MiniMax**（服务端 `/tts` 出 mp3，**页面可选男/女声** male-qn-qingse / female-tianmei，默认女声；`MINIMAX_VOICE_ID` 可覆盖默认）→ 失败回退浏览器 TTS。
- `voice/bridge.py` 起本地服务（`/questions /token /tts /answer /done`），密钥只在服务端、不进浏览器。
- `web/index.html`：像打电话——自动朗读问题 → 自动聆听 → 停顿即进下一题；同步显示文字 + 完整对话历史。
- 收尾：答案写出到 out 文件 → agent 读它提炼写画像。
- 没 Python 时语音不可用，其余功能照常。

## 6. 隐私与安全

- 核心全程本地：vault 在用户机器（mac 默认 iCloud Obsidian 目录），agent 直接读写。
- 语音密钥仅存 `~/.second-brain-obsidian/secrets.env`（chmod 600），绝不进 vault / git / 页面；语音作答只向用户自有 Azure / MiniMax 传问题文本与回答音频。
- 提炼时对疑似密钥 / token 脱敏，不写进库。vault 即「数字化的你」，妥善保管。

## 7. 跨平台

- macOS / Windows 都支持。默认库位置 mac=iCloud Obsidian 目录、Windows=`~/Documents`。
- 语音后台派生两平台适配（POSIX setsid / Windows DETACHED_PROCESS）；命令里 `python3` 在 Windows 用 `python` / `py`。

## 8. 锁定决策

| 项 | 决策 |
|---|---|
| 设计原则 | 奥卡姆（简、手动低频）+ 费曼（采访讲清 → 分析补缺）|
| 实现模型 | agent-native：vault 读写由 agent 直接做（markdown，按 `vault-format.md`）；自动提炼（默认开）+ 语音需 Python |
| 流程 | 建库 → 采访 → 写画像；更新靠在场提炼；读取靠原生 `CLAUDE.md`/`AGENTS.md` |
| 会话分析源 | Claude Code `/insights`；Codex / Hermes 在场提炼（都不读本地 transcript）|
| 知识结构 | 四层（Inputs/Process/Outputs/Feedback）一级目录 × 六大工作模式按需中文子目录；行业映射页；写入按自动判位 |
| 语音 | Azure STT + MiniMax TTS（男/女声可选，默认女声），打电话式，同步文字 + 对话历史；密钥仅 `secrets.env`；可选·用 Python |
| vault | agent 建 / 复用独立 vault，统一一份画像 + 知识 + MOC |
| 跨平台 | macOS / Windows |
