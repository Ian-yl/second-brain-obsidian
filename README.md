# second-brain-obsidian

> 把「**你是谁**（人格画像）+ **你知道什么**（知识库）」沉淀进 Obsidian，让任何 AI agent 用**你的风格 + 你的知识**做事——越用越像你。

一个 **agent-native** 的「第二大脑」skill：核心由 agent 直接读写 Obsidian markdown 完成，**不依赖 Python**。三家 agent（**Claude Code / Codex / Hermes**）共用同一份 vault。

落地页：<https://second-brain-obsidian.pages.dev>

## 它能做什么

- **人格画像 + 知识库 → 一份 Obsidian vault**：6 维度画像 + Inputs / Process / Outputs / Feedback 四层知识，agent 直接读写 markdown。
- **跨 agent 通用**：Claude Code 原生读 `CLAUDE.md`、Codex / Hermes 读 `AGENTS.md`（同内容），共用同一份 vault、互不冲突。
- **本地自动提炼**（默认开）：每次对话后，后台用**当前会话的 agent** 把关于你的新信息提炼进 vault。
  - 两种时机，**初始化时选、随时可切**（跟 agent 说「改成实时更新」/「结束对话再更新」即可）：
    - `end` —— 会话结束提炼一次（省）
    - `stop` —— 每条回复后增量提炼（实时、更稳）
  - **任何话题都收**（含项目、闲聊里关于你的真实信息）；明文密钥 / token 自动脱敏。
  - **纯本地、零外传**：只写你电脑里的 markdown，不上传任何东西。
- **实时语音问答**（可选）：像打电话一样答采访题——Azure STT 听写 + MiniMax TTS 朗读（男 / 女声可选，默认女声）。

## 快速开始

1. 装好 skill（落地页有邀请码 + 一键安装脚本）。
2. 在 agent 里说 **「初始化第二大脑」** → agent 会：建 vault → 人格问答（文字或语音）写画像 → 问你自动提炼时机并开好。
3. 之后正常聊天即可，第二大脑在后台自动长。任何项目里说 **「加载第二大脑」** 就能调用你的画像 + 知识。

常用：喂资料「收录这个链接」/「整理收件箱」/「体检知识库」；关闭自动提炼 `python3 scripts/install.py --remove`。

## 自动提炼 · 三家 agent 怎么触发

| Agent | `end`（会话结束一次） | `stop`（每条回复） |
|---|---|---|
| Claude Code | `SessionEnd` | `Stop` |
| Codex | `SessionEnd` | `Stop` |
| Hermes | `on_session_finalize` | `on_session_end` |

> 提炼引擎默认用**当前会话的 agent**（`claude -p` / `codex exec` / `hermes -z`）；想强制某个引擎，把引擎名或完整命令写进 `~/.second-brain-obsidian/engine`。Hermes 首次需 `hermes --accept-hooks` 同意 shell hook、并先 `hermes model` 配好模型。

## 结构

```
SKILL.md                       # agent 编排指令（建库 / 采访 / 读取 / 更新 / 知识维护）
references/                    # vault 写入规范 + 人格框架 + 安装配置
agents/openai.yaml             # Codex 清单
scripts/
  install.py / hook_entry.py   # 注册本地 hook + 后台提炼
  voice/                       # 打电话式语音采集（bridge.py + web/index.html）
<vault>/                       # 你的第二大脑
  用户画像.md  CLAUDE.md  AGENTS.md  _索引.md
  Knowledge/{Inputs,Process,Outputs,Feedback}/   Inbox/
```

## 隐私

核心全程本地：vault 在你机器上；提炼子 agent 带 `--strict-mcp-config`（不加载任何 MCP）；密钥只存 `~/.second-brain-obsidian/secrets.env`（chmod 600），绝不进 vault / git / 页面；提炼时明文密钥自动脱敏。和 HelixMesh 无关——它只是下载本 skill 的平台。

设计细节见 [`docs/specs/`](docs/specs/)。
