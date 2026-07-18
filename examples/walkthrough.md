# walkthrough — 用假数据走一遍 expert-blindtest 循环

全程假数据(MV EXAMPLE STAR / 整数示例值),演示「用户贴一条带专家换算值的成交 → 盲测 → 录点 → 回归更新」的完整闭环。你的领域换成你的标的和基准码,形状不变。

## 1. 用户贴料

> 「录一下:MV EXAMPLE STAR 75,000 dwt / 2015 built, dely {{某北亚港}} 20-22 {{月}}, redely {{某区域}}, $12,000/day (broker eqv 11,500 {{基准码 P-X}})」

行里出现 `eqv` + 基准码 → **expert-blindtest MUST 自动触发**(不是「要不要跑一下」,是必须)。

## 2. 先盲算(专家数对引擎不可见)

AI 解析出:标的 = MV EXAMPLE STAR(75k / 2015)、原始成交价 12,000、交接港与基准航线的位置差、无特殊机制标记(非回溯交接)。调引擎:

```bash
python3 tools/{{your_engine}}/blindtest.py \
  --subject "EXAMPLE STAR" --dwt 75 --built 2015 --raw-value 12000 \
  --dely "{{某北亚港}}" --route {{P-X}} --expert-equiv 11500
```

引擎输出(专家值只在最后对比时揭开):

```
位置项: −300   (交接港偏离基准航线起点,回归系数换算)
标的因子: −150 (75k vs 基准规格的引擎对表差)
盲算换算值 = 12,000 − 300 − 150 = 11,550
```

## 3. 对比 + 归因

```
盲算: 12,000 − 300(位置) − 150(标的因子) = 我的 {{P-X}}e 11,550
broker eqv = 11,500 → 偏差 +50 (+0.4%) ✓带内
→ 已录标定点(库存 43 点)
```

偏差 0.4%,带内。假如偏差是 −8%:不硬调系数,按序排查——①特殊机制漏判?(回溯交接不该剥位置项)②对方自报参数有水分?③引擎基准卡陈旧?④专家自己错了?结构性发现才出新规则。

## 4. 录标定点

引擎自动 upsert 进标定库:

```sql
INSERT INTO calib_points(date, subject, raw_value, expert_equiv, blind_equiv,
                         route, source)
VALUES('{{2026-01-15}}', 'EXAMPLE STAR', 12000, 11500, 11550,
       '{{P-X}}', 'broker live quote + blindtest');
```

## 5. 回归更新(定期,非每条)

标定点攒到一定量(或每周),重跑位置回归:

```bash
python3 tools/{{your_engine}}/position_regression.py --min-points 30
# → 位置分成系数 0.62 → 0.64(43 点样本),写回引擎配置
```

下一条盲测自动用新系数——**引擎在可验证地变准**,这就是飞轮的一圈。

## 这一圈留下了什么

1. 标定库 +1 点(回归原料)
2. 引擎可信度记录 +1(带内命中)
3. 若有结构性发现 → skill 禁手区 / 引擎规则 +1 条,memory feedback +1 条
4. 用户得到一行可核对的输出,全程零打扰

三个月后回看:标定点从 0 到几百,盲算偏差从 −10% 收敛到 ±2% 以内——每一条专家数都变成了你自己的引擎精度。
