# Vault 写入格式（agent-native 权威规范）

> **没有 Python 时，agent 直接读写本 vault 就靠这份规范**——严格照它写，产出跟 Python 脚本**字节级一致**，两条路互通、混用不乱。
> `<vault>` = 库根目录（init 时定）。所有日期用**本地当天** `YYYY-MM-DD`。

## 目录布局
```
<vault>/
  用户画像.md            # 人格画像（单文件）
  CLAUDE.md / AGENTS.md  # 画像摘要（两份同内容）；Claude Code 读 CLAUDE.md、Codex 读 AGENTS.md，进 vault 原生自动读
  _索引.md               # 知识 MOC 索引
  Knowledge/
    Inputs/  Process/  Outputs/  Feedback/   # 四层，每层下放 <slug>.md
  Inbox/                 # 速记收件箱（可选）
```

## 1. `用户画像.md`
frontmatter + **固定 8 段（顺序不可变，空段也保留标题）**：
```
---
type: user-profile
updated: <YYYY-MM-DD>
framework_version: 1
tags: [<标签>, ...]            # 内联列表，形如 性格/完美主义、风格/简洁直接
---

## 概览
<一两句总览；没有就写「（待补充）」>

## 性格特质
- <一句话特征>

## 价值观 / 做事原则
## 沟通 / 说话风格
## 思维 / 做事方式
## 行为处事 / 待人接物
## 偏好与禁忌

## 变更日志
- <YYYY-MM-DD> · [<维度>] <内容> · 来源 <source>
```
- **6 个维度名固定、别改字**：`性格特质` / `价值观 / 做事原则` / `沟通 / 说话风格` / `思维 / 做事方式` / `行为处事 / 待人接物` / `偏好与禁忌`。每段 0+ 条 `- ` 要点。
- **合并规则（跟 Python 一致）**：
  - 加一条特征 → 进对应维度段，**先去重**（跟已有要点意思重复就别加）再 append `- <内容>`。
  - 修正既有 → 找意思相近的那条**替换**，找不到就 append。
  - 每加/改一条 → `变更日志` append 一行（日期·`[维度]`·内容·`来源 <source>`），日志**只留最近 50 条**。
  - 新标签并进 frontmatter `tags`（去重）；动过就把 `updated` 设成当天。

## 2. `Knowledge/<层>/<slug>.md`
```
---
type: knowledge
layer: <Inputs|Process|Outputs|Feedback>
created: <YYYY-MM-DD>
updated: <YYYY-MM-DD>
aliases: [<别名>, ...]
tags: [<领域/xx>, <类型/xx>, 层/<层>]      # tags 必含 层/<层>
sources: [<source>, ...]
---

# <标题>

<正文>

相关：[[<相关笔记标题>]] [[...]]
```
- **四层归类**：Inputs=素材/来源/收集到的；Process=思考/方法/在做的；Outputs=产出/决策/结论；Feedback=复盘/教训/洞察。拿不准默认 `Inputs`。
- **slug** = 标题去掉 `\ / : * ? " < > |` 与空格（连续替换成 `-`）、≤60 字；文件名 `<slug>.md` 放对应层目录。
- **`相关：` 行**：只有有 links 时才加。
- **去重/合并**：先**跨四层找同 slug** 的笔记——有 → 合并（`tags`/`aliases`/`sources` 取并集、保留原 `layer`、`updated`=今天、正文**不重复段落**才 append）；无 → 新建。

## 3. `CLAUDE.md` + `AGENTS.md`（vault 根·原生自动加载）
画像每次变都**同步重写这两个文件，内容完全相同**——Claude Code 原生读 `CLAUDE.md`、Codex 原生读 `AGENTS.md`：
```
# 我的第二大脑

> 你正在我的「第二大脑」vault 里。请 **像我一样** 思考、表达、做决策——用我的风格、守我的原则。

## 我是谁
<概览正文>

### <非空维度名>
- <要点>

## 我的知识库
- 完整画像：[[用户画像]]
- 知识结构（Inputs/Process/Outputs/Feedback 四层）与索引：[[_索引]]
- 需要细节时查 `Knowledge/` 下对应四层目录。
```
（`### 维度` 只列**有内容**的维度。）

## 4. `_索引.md`（MOC·每次入库后重建）
```
---
type: moc
updated: <YYYY-MM-DD>
---

# 第二大脑 · 索引

- 人格画像：[[用户画像]]
- 知识笔记：<N> 篇

## 知识结构（Inputs / Process / Outputs / Feedback）

### Inputs · 输入·素材与来源（<n>）
- [[<slug>]]
### Process · 过程·思考与方法（<n>）
### Outputs · 产出·成果与决策（<n>）
### Feedback · 反馈·复盘与洞察（<n>）

## 按更新时间（dataview）

​```dataview
TABLE layer, updated FROM "Knowledge" SORT updated DESC
​```
```

## frontmatter 语法
- 标量：`key: value`；列表：`key: [a, b, c]`。值里含 `, [ ] : #` 或首尾空格的，用双引号包：`"v"`。
