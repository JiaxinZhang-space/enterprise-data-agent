# Enterprise Data Analysis Agent

一个面向技术作品集的企业经营分析 Agent。当前只完成 Day 1 的最小纵向闭环：

```text
自然语言问题 -> 规则路由 -> Metrics / 本地知识检索 -> 可追溯结果
```

当前实现是可测试基线，不代表 LangGraph、向量 RAG、FastAPI、PostgreSQL 或自由 Text-to-SQL 已经完成。

## 已验证的 Day 1 能力

- 对“错配率定义”问题选择知识检索路径，并返回本地来源。
- 对“2026 年 9 月 A 场错配率及 8 月环比”选择 Metrics 路径。
- 用固定 SQL 模板和参数绑定查询 SQLite 合成数据。
- 返回工具路径、SQL、参数、数据与限制说明。
- 对写操作意图进行前置拒绝。

## 运行

项目本身在 Day 1 不依赖第三方包。使用 Python 3.11+：

```powershell
python -m unittest discover -s tests -v
python scripts/run_demo.py --reset "2026年9月A场的错配率是多少，比8月提高了多少个百分点？"
python scripts/run_demo.py "错配率是怎么计算的？"
python scripts/run_demo.py "DELETE FROM dwd_breeding_event"
```

当前电脑的 Python 未加入 PATH 时，可显式使用已发现的解释器：

```powershell
& "C:\Users\Zhang\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -m unittest discover -s tests -v
```

## 当前目录

```text
app/                    核心路由、工具和服务编排
data/knowledge/         模拟业务规则与指标口径
data/synthetic/         固定种子的合成事件
docs/                   计划、决策和学习卡片
scripts/                初始化与演示入口
tests/                  自动化测试
```

完整范围、14 天路线和边界见 `智能问数 Agent｜项目交接与 Codex 执行说明.md`。

第一次接触项目目录时，请先看 [`docs/beginner_guide.md`](docs/beginner_guide.md)。它用非前后端术语解释每个目录，并提供亲自运行的两条命令。


