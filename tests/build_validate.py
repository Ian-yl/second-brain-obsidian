#!/usr/bin/env python3
"""DEV / CI spec 自检 —— **不是运行时组件**。

按 `references/vault-format.md` 在临时目录实建一个示例 vault（产品经理场景）+ 校验结构自洽：
frontmatter 可解析 / 6 张 MOC 链接对得上 / 知识 tags 含 层+模式 / 路径与 mode 一致 / 无断链。

跑：`python3 tests/build_validate.py`  —— 通过 exit 0，发现问题 exit 1。

⚠️ skill 运行时是**零依赖**（除可选语音）——用户正常用第二大脑**不需要**此脚本；它只在开发期
校验 spec 能否建出自洽的库（曾抓到过 00-Home 的 Domain 断链）。模板需与 vault-format 同步维护。
"""
import os, re, sys, shutil, tempfile

MODES = ["研究分析", "项目交付", "客户个案", "内容生产", "流程运营", "学习成长"]
MODE_ID = {"研究分析": "research-analysis", "项目交付": "project-delivery", "客户个案": "case-management",
           "内容生产": "content-production", "流程运营": "operations", "学习成长": "learning-growth"}
L1 = ["00-Inbox", "10-Inputs", "20-Process", "30-Outputs", "40-Feedback", "50-MOCs",
      "60-Domains", "70-Assets", "90-Archive", "_System/Templates", "_System/Dashboards", "_System/Attachments"]


def build(root):
    def w(path, body):
        full = os.path.join(root, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        open(full, "w", encoding="utf-8").write(body)

    for d in L1:
        os.makedirs(os.path.join(root, d), exist_ok=True)

    w("用户画像.md", "---\ntype: user-profile\nupdated: 2026-06-30\nframework_version: 1\n"
      "tags: [性格/完美主义, 风格/简洁直接]\n---\n\n## 概览\n质量优先的产品实干者。\n\n"
      "## 性格特质\n- 完美主义\n\n## 价值观 / 做事原则\n## 沟通 / 说话风格\n## 思维 / 做事方式\n"
      "## 行为处事 / 待人接物\n## 偏好与禁忌\n\n## 变更日志\n- 2026-06-30 · [性格特质] 完美主义 · 来源 采访\n")

    summary = ("# 我的第二大脑\n\n> 你正在我的「第二大脑」vault 里。请 **像我一样** 思考、表达、做决策。\n\n"
               "## 我是谁\n质量优先的产品实干者。\n\n### 性格特质\n- 完美主义\n\n"
               "## 我的知识库\n- 完整画像：[[用户画像]]\n- 总入口与索引：[[00-Home]]\n")
    w("CLAUDE.md", summary)
    w("AGENTS.md", summary)

    moc_links = "\n".join(f"- [[MOC - {m}]]" for m in MODES)
    w("00-Home.md", f"---\ntype: home\nupdated: 2026-06-30\n---\n\n# 第二大脑 · 总入口\n\n"
      f"## 🧭 从这开始\n- 人格画像：[[用户画像]]\n\n## 六大工作模式\n{moc_links}\n\n"
      "## 常用领域\n- [[product]]\n\n## 最近输出 / 复盘\n```dataview\n"
      'TABLE mode, updated FROM "30-Outputs" OR "40-Feedback" SORT updated DESC LIMIT 10\n```\n')

    for m in MODES:
        w(f"50-MOCs/MOC - {m}.md", f"---\ntype: moc\nmode: {MODE_ID[m]}\nupdated: 2026-06-30\n---\n\n"
          f"# MOC · {m}\n\n## Inputs\n## Process\n## Outputs\n## Feedback\n")

    w("60-Domains/product.md", "---\ntype: domain\ndomain: product\nupdated: 2026-06-30\n---\n\n"
      "# 产品经理\n\n## 常用工作模式\n- 主：项目交付\n- 辅：研究分析\n\n## 推荐入口\n- [[MOC - 项目交付]]\n")

    notes = [("10-Inputs/研究分析", "2026-06-30 - 用户反馈", "Inputs", "研究分析"),
             ("20-Process/项目交付", "2026-06-30 - PRD 草稿", "Process", "项目交付"),
             ("40-Feedback/项目交付", "2026-06-30 - 上线复盘", "Feedback", "项目交付")]
    for folder, title, layer, mode in notes:
        w(f"{folder}/{title}.md", f"---\ntype: knowledge\nlayer: {layer}\nmode: {MODE_ID[mode]}\n"
          f"domain: product\ncreated: 2026-06-30\nupdated: 2026-06-30\naliases: []\n"
          f"tags: [领域/product, 类型/事实, 层/{layer}, 模式/{mode}]\nsources: [用户明说]\n---\n\n# {title}\n\n正文。\n")
    w(".obsidian/app.json", "{}")


def frontmatter(path):
    t = open(path, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n", t, re.S)
    if not m:
        return None
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.strip().startswith("#"):
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip()
    return fm


def validate(root):
    issues = []
    allmd = [os.path.join(dp, f) for dp, _, fs in os.walk(root) for f in fs if f.endswith(".md")]
    filemap = {os.path.splitext(os.path.basename(p))[0]: p for p in allmd}

    for p in allmd:
        rel = os.path.relpath(p, root)
        if os.path.basename(p) in ("CLAUDE.md", "AGENTS.md"):
            continue  # 指令文件·本就无 frontmatter
        fm = frontmatter(p)
        if fm is None:
            issues.append(f"[frontmatter缺失] {rel}")
            continue
        if "type" not in fm:
            issues.append(f"[无 type] {rel}")
        if fm.get("type") == "knowledge":
            tags = fm.get("tags", "")
            if "层/" not in tags:
                issues.append(f"[tags 缺 层/] {rel}")
            if "模式/" not in tags:
                issues.append(f"[tags 缺 模式/] {rel}")
            for m in MODES:
                if f"/{m}/" in rel and fm.get("mode") != MODE_ID[m]:
                    issues.append(f"[路径模式≠mode] {rel}: {m} vs {fm.get('mode')}")

    home = open(os.path.join(root, "00-Home.md"), encoding="utf-8").read()
    for m in MODES:
        if f"[[MOC - {m}]]" not in home:
            issues.append(f"[00-Home 缺 MOC 链接] {m}")
        if not os.path.exists(os.path.join(root, f"50-MOCs/MOC - {m}.md")):
            issues.append(f"[MOC 文件不存在] {m}")

    for p in allmd:
        for tgt in re.findall(r"\[\[([^\]|]+)", open(p, encoding="utf-8").read()):
            if tgt not in filemap:
                issues.append(f"[断链] {os.path.relpath(p, root)} → [[{tgt}]]")
    return issues


def main():
    root = tempfile.mkdtemp(prefix="sbo-spec-test-")
    try:
        build(root)
        issues = validate(root)
        n = len([1 for dp, _, fs in os.walk(root) for f in fs if f.endswith(".md")])
        print(f"建库：{n} 个 md 文件")
        if issues:
            print(f"⚠️ {len(issues)} 个问题：")
            for i in issues:
                print(" -", i)
            return 1
        print("✅ 全部通过：frontmatter 可解析 / 6 MOC 链接对得上 / tags 含层+模式 / 路径与 mode 一致 / 无断链")
        return 0
    finally:
        shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
