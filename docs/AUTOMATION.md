# AUTOMATION.md — 定时任务 / 夜批 / AI 夜审模式

自动化层的定位:**机器做苦力,AI 做审核,人只守承重决策。** 四个模式,从简到繁。

## 模式一:定时任务(macOS launchd 示例)

plist 骨架(放 `~/Library/LaunchAgents/com.{{yourdesk}}.{{jobname}}.plist`):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>com.{{yourdesk}}.{{jobname}}</string>
  <key>ProgramArguments</key>
  <array>
    <string>{{/path/to/your/venv}}/bin/python3</string>
    <string>{{/path/to/workspace}}/periodic_jobs/{{jobname}}/run.py</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict><key>Hour</key><integer>8</integer><key>Minute</key><integer>0</integer></dict>
  <key>StandardOutPath</key><string>{{/path/to/workspace}}/logs/{{jobname}}.log</string>
  <key>StandardErrorPath</key><string>{{/path/to/workspace}}/logs/{{jobname}}.err.log</string>
</dict>
</plist>
```

装载:`launchctl load ~/Library/LaunchAgents/com.{{yourdesk}}.{{jobname}}.plist`

**注意点(都是实战踩出来的)**:

1. **入口用有磁盘权限的 python,不用 bash。** macOS 对 Desktop / Documents 有 TCC 权限管制:launchd 起的 bash 没有 Full Disk Access,读这些目录会静默失败(exit 126),任务连断多日都没人发现。给你的 python 解释器授 Full Disk Access,plist 入口直接指它;`.sh` 只留手动跑。
2. **每轮成功写心跳文件**(如 `logs/<job>_last_success.txt` 写时间戳)。监控只需查「心跳距今超 N 小时 → 告警」,比解析日志可靠。
3. **改 / 装 / 卸任何系统级定时任务,先通知用户**(见 CLAUDE.md 破坏性操作守则)。
4. Linux 用 cron / systemd timer,同样原则:绝对路径、独立日志、心跳。

## 模式二:夜批 loop(扫数据 → 计算 → 落库)

适用:数据量大、单条处理成本高、白天不想占机器的活。

```
run.py 每晚定时:
  1. 扫源(新到文件 / DB 里 status='pending' 的行)
  2. 逐条计算(解析 / 换算 / 打分)——单条失败记 failed 原因,不中断整批
  3. 落库(upsert,幂等键设计好:重跑不翻倍)
  4. 写批次摘要(处理 N 条 / 成功 X / 失败 Y + 原因分布)+ 心跳
```

要点:**幂等**(同一批重跑结果一致)、**单条隔离**(一条坏数据不拖死整批)、**dead-letter**(失败条目留在队列里带原因,下轮或人工重试)、**陈旧门**(源数据超 N 天的丢弃或标陈,不静默入库)。

## 模式三:AI 夜审(机器产物 → 专家实例复核)

夜批只保证「算了」,不保证「算对」。解析错一个字段、单位读错一档,静默落库后会污染下游判断。解法:**另起一个 AI 实例,以 top expert 身份审机器产物,疑点写回 DB + 出日报。**

```
夜批 loop 完成
  │
  ▼
审核脚本取当批产物(如当晚新增的 N 条计算结果)
  │
  ▼
headless 调用 AI(CLI 示例):
  claude -p "你是{{领域}}资深专家。审核以下今晚批处理产物,逐条检查:
    ① 数值是否在合理值域(如 {{指标}} 应在 {{下限}}-{{上限}})
    ② 单位/口径是否读错档(如 $/mt 与 $/day 混淆)
    ③ 与同类历史记录是否离群
    输出 JSON: [{id, verdict: ok|suspect, reason}]
    <产物 JSON 粘贴或指路径>"
  │
  ▼
suspect 条目 → 写回 DB(status='suspect' + reason,不删不改原值)
  │
  ▼
日报:当批 N 条 / 疑点 X 条 + 逐条一句话,推给用户
```

设计要点:

- **审核与生产解耦**:审核实例只读产物,不碰生产逻辑;它的输出是「疑点标注」,不是「静默修正」——改数的决定留给人或白天的主线会话。
- **给审核实例领域人设 + 检查清单**:泛泛「检查一下」审不出东西;值域、口径、离群三类检查写死在 prompt 里。
- **疑点必须留痕**:写回 DB 带 reason,日报可追溯。审核发现的系统性错误(不是单条噪声)→ 回写成生产脚本的校验规则,下批自动挡。
- 用 CLI 订阅额度跑 headless 时,确认环境里没有按次计费的 API key 变量,避免走错计费路径;高频小审核可换本地模型(如 Ollama)。

## 模式四:增量同步(状态文件记 offset)

适用:持续增长的源(邮件箱 / 日志 / 别人维护的 DB)要持续搬进自己的库。

```
state.json: {"last_offset": "...", "last_run": "...", "last_id": "..."}

每轮:
  1. 读 state 拿上次位置
  2. 只取增量(id > last_id / mtime > last_run)
  3. 处理 + 落库(幂等)
  4. 全部成功才更新 state ——半途失败下轮从旧位置重扫,配合幂等不产生重复
```

要点:state 更新放在**批次成功之后**(宁可重扫,不可漏扫);state 文件和数据同目录并入 `.gitignore`;偶尔全量校核一次(增量逻辑有 bug 时能发现漏洞)。

## 组合起来的典型夜间节拍

```
{{22:00}} 增量同步:把白天新到的源数据搬进库
{{23:00}} 夜批 loop:计算 / 打分 / 换算,落库
{{07:30}} AI 夜审:审昨晚产物,疑点写回 + 日报
{{08:00}} 晨间摘要:给用户一条「昨晚处理了什么 + 几个疑点待你裁决」
```

每一环独立心跳、独立日志;上游失败下游能感知(查心跳)而不是拿着空数据硬跑。
