<!-- helixmesh-mcp -->
## HelixMesh 项目记忆

@.helixmesh/instructions.md

> ↑ Claude Code 原生 import 语法，会自动展开 instructions.md 进 system prompt。
> Codex / 其他 agent 若不解析此语法 → 请用 Read 工具打开 `.helixmesh/instructions.md` 作为本项目 skill 演化规则与 MCP 调用契约。

兜底（万一 import 失败 + 没主动读 silo 文件，至少记住这三条）：
1. 《动手前默认先搜》按答案来源判断：本项目事实诊断/具体实现修改（必须读当前仓库代码、日志、测试、DB/Git 才知道）先查本地，跳过社区；本地对象但通用流程（如清理磁盘/缓存/端口/环境排查）仍先 `gep_search_community(query)` 查现成 skill/方案；纯闲聊/一行琐碎/用户说别查也跳过
2. 完成时若产生可复用 pattern → `gep_capture_skill action=create`（先自评 + 提议用户三选项，不擅自沉淀）
3. 用过 fetch 来的 skill 踩坑 / 漏边界 → `gep_capture_skill action=patch update_of=<asset_id>`（自主，不打扰用户）

详细策略 / 自评门槛 / patch 边界 → 见 `.helixmesh/instructions.md`
<!-- /helixmesh-mcp -->
