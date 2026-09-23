# Skills Index

本索引指向可复用的 Skills——AI 可以调用的工作流、工具和最佳实践。

- **想使用某个能力** → 浏览下方条目,打开对应 skill
- **第一次用这套模板** → 先读 `docs/QUICKSTART.md`
- **想添加新 skill** → 照 `docs/SKILL_AUTHORING.md` 规范写,建完**必须**回到这里加一行 + 在 `CLAUDE.md` 硬触发区挂触发词(skill 建完必接触发点,否则等于不存在)

---

## 本仓自带示例 skills(`.claude/skills/`)

- [**pricing-anchor**](../../.claude/skills/pricing-anchor/SKILL.md) — 任何报价/评审动作前强制先锚市场价 level:定价格族 → peer 锚价 → 只调可量化差 → 才 propose。触发:任何交易标的的 propose / 评审 / 报价,或用户问「能做到多少 / 该报什么 / 这价合理吗」。假数据走查:`examples/walkthrough_pricing_anchor.md`。
- [**expert-blindtest**](../../.claude/skills/expert-blindtest/SKILL.md) — 带专家换算值的数据出现时自动跑盲测循环:先盲算(不看专家数)→ 对比偏差 → 归因 → 录标定点 → 偏差超阈排查出规则。触发:用户贴的数据行里出现专家 equivalent / 换算值标注。假数据走查:`examples/walkthrough.md`。
- [**voyage-estimator**](../../.claude/skills/voyage-estimator/SKILL.md) — 航次估算(dry bulk 示例):V3.5 公式批量算 TCE / 航次 P&L / breakeven,先查历史 comp 再算、算完回流入库。触发:「算航次 / 算 TCE / voyage calc / 这票货哪条船好」。
- [**knowledge-flywheel**](../../.claude/skills/knowledge-flywheel/SKILL.md) — 知识积累飞轮:外部知识 / 教训 / 复盘 → 蒸馏 → INBOX 候选 → 定期晋升进 KB + memory。触发:学到新领域知识、复盘出教训、同一问题第二次出现。

---

## 你自己的 skills(照条目格式补充)

- [**{{skill-name}}**]({{路径}}) — {{一句话:做什么 + 怎么做的要点}}。触发:{{触发词 / 触发场景,写具体的用户原话模式}}。
