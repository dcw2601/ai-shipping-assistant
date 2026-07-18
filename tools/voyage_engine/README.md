# voyage_engine — 航次估算引擎接口文档(V3.5 公式)

**本模板只带接口文档,引擎代码由仓主自行放入本目录**(纯函数实现即可,无外部依赖需求)。公式经实战多轮交叉验证(V2↔V3.5 零偏差、多组基准案例),照抄实现可复现。

## 输入结构

```python
vessel = {
    "name": "MV EXAMPLE STAR",
    "dwt": 75000,            # 载重吨
    "built": 2015,
    "ballast_spd": 12.5,     # 空放航速 kn
    "laden_spd": 11.5,       # 重载航速 kn
    "cons_ballast": 24.0,    # 空放主机油耗 mt/day
    "cons_laden": 26.0,      # 重载主机油耗 mt/day
    "cons_idle": 3.0,        # 港内待泊油耗 mt/day
    "cons_work": 3.5,        # 港内作业油耗 mt/day
    "cons_sub": 0.1,         # 辅机(MGO)mt/day
}

config = {
    "qty": 73000,            # 货量 mt(常用默认: dwt − 2000)
    "freight_rate": 10.0,    # 运价 $/mt(示例值,替换为你的 desk 口径)
    "hire": 12000,           # 日租金 $/day(示例值)
    "vlsfo_price": 500,      # $/mt(示例值)
    "mgo_price": 800,        # $/mt(示例值)
    "margin_days": 1.0,      # 余量天数(摊进海上时间)
    "ports": [               # 港序,按顺序 2-8 个
        {"type": "Ballast",  "name": "{{起始港}}", "dist": 500,  "wf": 0.05, "idle": 0.5, "ld_rate": 0,     "pc": 0},
        {"type": "Loading",  "name": "{{装港}}",   "dist": 0,    "wf": 0,    "idle": 1.0, "ld_rate": 20000, "pc": 50000},
        {"type": "Dischg.",  "name": "{{卸港}}",   "dist": 2000, "wf": 0.05, "idle": 1.5, "ld_rate": 15000, "pc": 60000},
    ],
    # 每港: dist=距上一港海里; wf=天气系数; idle=待泊天; ld_rate=装卸率 mt/day(仅装卸港); pc=港费 USD
    # 港费/装卸率为示例整数,一律替换为你的三合法来源(权威费率表/自家库/用户口径)
    # port type 支持: Ballast / Loading / Dischg. / Bunker / Passing / Canal
    "commissions": {"add_comm": 0.0125, "brokerage": 0.0375},   # 示例比率
    "fixed_costs": {"cev": 2000, "ilohc": 5000, "bb": 0},        # 杂项固定费,示例值
}
```

## 核心公式

### 时间

```
Sea Days (leg i) = dist_i / (speed_i × 24) × (1 + WF_i)
  speed_i = ballast_spd 若该 leg 在第一个 Loading 港之前,否则 laden_spd
  (Passing/Bunker/Canal 在首个 Loading 之后的都按 laden)

Work Days (port p) = qty / ld_rate_p   (仅 Loading/Dischg. 港)

Total Sea Days = Σ sea days × margin_factor
  margin_factor = (raw + margin_days) / raw   (margin 只摊海上时间,不加港内)

Total Duration = Total Sea Days + Σ idle + Σ work
```

**口径警告**:天气系数是 `×(1 + WF)`,**不是** `/(1 − WF)`。两种口径在 WF=10% 时差约 1%,长航线复利放大——这是历史上盲算 vs 报表偏差的头号来源。接外部数据时先确认对方用哪种口径再换算。

### 燃油

```
主机 VLSFO = Σ_leg (sea_days × cons_leg) + Σ_port (idle × cons_idle + work × cons_work)
辅机 MGO   = Total Duration × cons_sub
Bunker Expense = VLSFO 吨数 × vlsfo_price + MGO 吨数 × mgo_price
```

(需要排放控制区 ECA 分油种时:每 leg / 每港按 ECA 标志把主机油耗切进 MGO 桶,结构同上。)

### P&L

```
Revenue    = qty × freight_rate
Op.Expense = 港费合计 + Bunker + Revenue×(add_comm + brokerage) + 固定杂项(cev/ilohc/bb) + dem/des
Op.Profit  = Revenue − Op.Expense
Total Hire = hire × Total Duration × (1 − hire 佣金率)

★ TCE        = Op.Profit / Total Duration     ($/day,与 hire 直接可比)
★ Voyage P&L = Revenue − Op.Expense − Total Hire
```

**硬校验**:`Voyage P&L = Revenue − Op.Expense − Total Hire` 必须严格相等(实现里独立算两遍对账)。

### Breakeven

```
breakeven_freight = 使 Voyage P&L = 0 的 freight_rate(线性,解析可解)
breakeven_hire    = 使 Voyage P&L = 0 的 hire
```

## 建议实现接口

```python
def estimate(vessel: dict, config: dict) -> dict:
    """返回 {duration, sea_days, port_days, vlsfo_mt, mgo_mt,
             bunker_cost, revenue, op_expense, tce, voyage_pnl}"""

def breakeven_freight(vessel, config) -> float
def breakeven_hire(vessel, config) -> float
def rank(vessels: list[dict], config) -> list[dict]   # 按 TCE 排序
```

## 自带 self-test

实现完先跑一组固定输入的黄金样例(把上面示例 vessel+config 的期望输出写死在测试里),任何改动后重跑——回归立刻能查出来。你的历史手算案例是最好的黄金样例来源。
