# AI Shipping Assistant — 航运人的 AI 执行幕僚系统模板

> 一个在真实 dry bulk 交易台上迭代出来的 **Claude Code 主场架构**,脱敏成可 fork 的模板。
> 它不是聊天机器人配置,是一套让 AI 成为「长期执行幕僚」的**工程结构**:身份层、认知纪律、三层记忆、技能生态、自动化节拍、防泄漏闸。
> Fork 后换掉身份层、填上你自己的 desk 数据,它就开始长成**你的**系统。

## 这套架构解决什么问题

裸用 AI 助手的三个死穴:**会话即生即灭**(昨天教的今天忘)、**没有纪律**(顺着你说、编数字)、**能力不沉淀**(同样的活每次从头教)。本模板的回答:

1. **文件就是记忆** — 跨会话的一切(规则/教训/事实)必须落盘;三层架构(L3 被动加载规则 / L1-L2 主动检索 / harness 索引)。
2. **认知纪律是地基** — `rules/EPISTEMICS.md` 每次会话强制加载:标注事实/推断/猜测、不知道就直说、先给反面、无新证据不让步、数据必核 asof。
3. **能力沉淀成 skill** — 每个可复用工作流固化成 `.claude/skills/` 一个目录,带触发词、流程、禁手清单、输出契约;做完一件事,下次更快。

## 快速开始(fork 之后)

1. **改身份层**:`rules/SOUL.md`(你的 AI 叫什么、什么性格)、`rules/USER.md`(你是谁、你的行业、你的要求)。全文搜 `{{` 把占位符换成你的值。
2. **读一遍 `CLAUDE.md`** — 它是根路由器,Claude Code 每次会话自动加载。按你的领域改「硬触发规则」区。
3. **建你的第一个 skill**:照 `docs/SKILL_AUTHORING.md` 的规范,把你手头最常做的一个工作流写成 skill。
4. **接数据**:`rules/WORKSPACE.md` 登记你的数据目录;skills 里的 `<your desk rates>` 类占位符填你的真实数字。
5. **上自动化**(可选):`docs/AUTOMATION.md` 讲 launchd/cron 定时任务 + 夜批 + AI 审核循环的模式。

## 目录地图

```
CLAUDE.md                 ← 根路由器(每会话自动加载;@import 身份三件套)
rules/
  SOUL.md                 ← AI 的身份与行为底色(模板,改成你的)
  USER.md                 ← 你的画像与操作要求(模板)
  EPISTEMICS.md           ← 认知纪律(通用,建议原样保留)
  COMMUNICATION.md        ← 沟通与写作风格约定
  WORKSPACE.md            ← 文件路由表(找文件先查这里)
  skills/INDEX.md         ← skill 总索引
.claude/skills/           ← skill 真源(每个 skill 一个目录)
docs/
  ARCHITECTURE.md         ← 整体架构与设计决策
  MEMORY_SYSTEM.md        ← 三层记忆系统详解
  SKILL_AUTHORING.md      ← skill 编写规范(触发/流程/禁手/输出契约)
  AUTOMATION.md           ← 定时任务/夜批/AI 夜审模式
tools/
  leak_scan.py            ← 发布前防泄漏全文闸(deny-list 命中即挡)
  voyage_engine/          ← 航次估算纯函数引擎(V3.5 公式,dry bulk 示例)
examples/                 ← 假数据走通的完整示例
```

## 设计原则(从实战里淬出来的)

- **准确高于认同**:AI 被质疑后,只有新事实才改口;被语气压住就附和 = 谄媚,禁止。
- **专业常数只有三个合法来源**:权威文件、自家数据库、用户口径。没有就标缺口,**绝不编一个看起来合理的数**。
- **skill 建完必接触发点**:没有触发词的 skill 等于不存在。
- **机器算 → 专家审 → 疑点留痕**:自动化产物要有独立审核层(可以是另一个 AI 实例当 top expert 夜审)。
- **破坏性操作三段式**:收集 → 沙盒 → 验证;永不 `rm`(用 mv 到回收站);对外发布先确认。
- **每一条外部专家的数,都是一次免费校准**:盲算 → 对比 → 录点 → 回归。

## 来源与致谢

架构在一个真实 commercial operator 的日常使用中迭代(fixture 定价、航次估算、市场分析、撮合)。所有公司数据、个人信息、邮件资料已移除;shipping 类 skill 保留方法论、参数换占位符。公理体系框架参考了 [grapeot 的公开整理](https://github.com/grapeot)。

License: MIT
