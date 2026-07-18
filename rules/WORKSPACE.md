# WORKSPACE.md — 文件路由表(模板)

目标:让 AI 每次 session 快速知道「去哪里找 / 放什么」。**找任何文件前先查这里,再搜索。** 发现新目录没被收录,顺手更新本表。

## 路由规则

| 内容类型 | 目录 | 说明 |
|---|---|---|
| 身份与规则 | `rules/` | SOUL / USER / EPISTEMICS / COMMUNICATION / 本表 |
| skill 真源 | `.claude/skills/<skill-name>/` | 每个 skill 一个目录,索引在 `rules/skills/INDEX.md` |
| 架构与规范文档 | `docs/` | 只放「怎么设计的 / 怎么写的」,不放业务数据 |
| 动态记忆 | `contexts/memory/` | L1/L2 观察记录,agent 主动检索 |
| 调研报告 | `contexts/{{survey_sessions}}/` | {{占位:每次深度调研一个文件}} |
| 每日 / 周期产物 | `contexts/{{daily_records}}/` | {{占位:日报、复盘等}} |
| 业务数据(不入 git) | `data/` | 数据库、导出文件——`.gitignore` 整目录忽略 |
| 一次性脚本 / 实验 | `{{adhoc_jobs}}/<project>/` | 临时项目,做完可归档 |
| 常驻工具脚本 | `tools/` | leak_scan、引擎、CLI 等 |
| 定时任务 | `{{periodic_jobs}}/` | launchd/cron 入口 + 各任务脚本,见 `docs/AUTOMATION.md` |

## 命名规则

- 目录和文件名:小写 + 下划线(snake_case)
- 临时一次性项目:`tmp_<name>/`
- 淘汰文件不删:`mv FILE FILE.deprecated_YYYYMMDD`

## Python 环境

- 根目录 `.venv/` 为工作区级环境;需要隔离时在子项目下建独立 venv
- 定时任务入口用**有磁盘权限的 python 解释器绝对路径**(见 `docs/AUTOMATION.md` 的坑)

## 本机区域(topology 示例,替换为你的)

```
{{~/your-workspace/}}
  ├── {{本仓库}}/            ← 主场:身份、规则、记忆、技能总根
  ├── {{数据管道项目}}/       ← 各自带自己的 CLAUDE.md,主场只放路由指针
  └── {{知识库 vault}}/       ← 长期知识层(如 Obsidian vault)
```

> 各子项目的运维细节写在子项目自己的 `CLAUDE.md`;本表只管「在哪」,不管「怎么用」。

<!-- 新增活跃项目按上面格式补充一行;一次性项目放 adhoc 目录,无需登记 -->
