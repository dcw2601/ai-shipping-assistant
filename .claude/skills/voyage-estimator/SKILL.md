---
name: voyage-estimator
description: 干散货航次估算(dry bulk 示例 skill)——按 V3.5 公式算航次时长、油耗、P&L、TCE、breakeven,支持多船同航线比选。触发:「算航次 / 航次估算 / 算 TCE / voyage calc / 这票货哪条船好 / breakeven 多少 / 比一下这几条船」,或用户贴出船舶 spec(速度+油耗)加运价要求估算时。引擎代码由仓主自行放入 tools/voyage_engine/(本模板只带接口文档)。
---

# voyage-estimator — 航次估算(V3.5)

给一票货 + 一条船(或一组船),算出:航次总天数、油耗与燃油成本、航次 P&L、TCE、breakeven 运价 / 租金。多船比选按 TCE 排名。

**引擎代码不在本模板内**——接口与公式见 `tools/voyage_engine/README.md`,照它实现或接你已有的引擎。本文件管工作流。

## 触发(MUST)

- 「算航次 / 航次估算 / 算 TCE / voyage calc / estimate profit」
- 「这票货哪条船好 / 比一下这几条船 / which vessel is best」
- 「breakeven 运价 / 最高能付多少 hire」
- 用户贴出船舶 spec(dwt / 速度 / 油耗)+ 运价或货盘,要求估算

## 流程

1. **先查 comp,再算**(铁律):同装 / 卸港的历史估算库里有 comp → 只调差异项(运价 / 油价 / 船参数),不从头拍;查不到显式报「已查,0 命中」再从头算。
2. **取船数据**:从用户粘贴 / 船位表解析;必备字段 `name, dwt, built, ballast_spd, laden_spd, cons_ballast, cons_laden, cons_idle, cons_work`。缺字段按船型段默认值补并**显式标注**(默认值表放你的 `references/`,用你 desk 的口径,别抄别人的)。
3. **校验物理合理性**:ballast/laden 速度是否颠倒(常见笔误,自动修并报)、油耗比是否离群、字段缺失。警告必须 surface 给用户。
4. **建航线配置**:港序(Ballast → Loading → 中间港 → Dischg.,支持 Bunker/Canal/Passing 类型)、每段距离、天气系数、装卸率、港费。距离与港费**只认三来源**(权威表 / 自家库 / 用户口径),没有就标缺口。
5. **算**(公式见 `tools/voyage_engine/README.md`)→ 交叉核:`Voyage P&L = Revenue − Op.Expense − Total Hire` 必须严格相等。
6. **算完回流**:结果 upsert 进估算库(幂等键 = 船+装港+卸港+laycan+日期,重跑不翻倍),让下一次有 comp 可查。
7. **呈现**:排名表(TCE / P&L / 时长关键列)+ 商业判断(头部尾部四分位、边缘船的 breakeven、数据质量警告、结论:fix 谁避开谁)。

## 校验阈值(值域闸)

| 检查 | 典型区间 | 动作 |
|---|---|---|
| 航次总天数 | 10–100 天 | <5 或 >150 → flag |
| 燃油成本/收入比 | 15–40% | >50% → flag |
| TCE | {{你的 desk 合理区间}} | 为负 → 显式标亏损 |
| 时长一致性 | 海上 + 港内 = 总 | 必须严格相等 |

## 禁手

- ❌ 跳过 comp 直查直接从头算(历史同航线估算是最好的锚)
- ❌ 编距离 / 编港费 / 编装卸率(三来源之外 = 缺口,不 = 可以拍)
- ❌ 天气系数用 `/(1−WF)` 口径混进 `×(1+WF)` 引擎(两种口径差 ~1%,长航线复利放大——见 README「口径」节)
- ❌ 算完不回流入库(飞轮断链)

## 输出契约

```
{{船名}}: 时长 {{d}} 天(海 {{x}} + 港 {{y}}) · 燃油 ${{...}} · TCE ${{...}}/day · P&L ${{...}}
breakeven: freight ${{...}}/mt(当前 hire 下) / hire ${{...}}/day(当前 freight 下)
[警告: {{数据质量 flag 逐条}}]
```
