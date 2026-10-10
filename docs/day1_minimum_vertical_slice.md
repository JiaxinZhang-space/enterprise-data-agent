# Day 1：项目初始化与最小纵向闭环

## 环境核对（2026-10-10）

- 当前目录初始只有交接说明，不是 Git 仓库。
- Docker CLI 29.2.0、Compose 5.0.2 已安装；Docker Desktop Linux 引擎未运行。
- `python`、`py`、`uv`、`pip` 未加入 PATH。
- 可用解释器：Codex bundled Python 3.12.14；本机 Python 3.13.7。
- 因 Docker 未启动，按交接说明先用 SQLite 跑通，PostgreSQL 留到 Day 2～3。

## 不超配的依赖策略

Day 1 核心闭环只用 Python 3.11+ 标准库：`sqlite3`、`json`、`argparse`、`unittest`。这样能先验证业务口径与工具边界，不把依赖安装问题和业务逻辑问题混在一起。

`pyproject.toml` 已记录后续按阶段安装的兼容范围，但这些可选依赖尚未安装或集成：

- API：FastAPI 0.x、Uvicorn 0.x、HTTPX 0.x。
- Agent：LangGraph 1.x。
- SQL：SQLGlot 27～29、SQLAlchemy 2.x、psycopg 3.x。
- RAG/UI：Chroma 1.x、Streamlit 1.x。
- 测试：pytest 8.x；Day 1 先用内置 `unittest` 保证无依赖可测。

实际接入每组依赖时再生成锁定结果并跑兼容测试；不能把版本清单当作已集成能力。

## 首批演示问题

1. “错配率是怎么计算的？”——知识检索，必须返回模拟指标文档来源。
2. “2026 年 9 月 A 场的错配率是多少，比 8 月提高了多少个百分点？”——Metrics，验证分子/分母和环比百分点。
3. “找出近三个月错配次数最多的 5 个场区，分品系比较。”——后续 SQL Tool，验证分组、Top N 和 Schema Linking。
4. “哪些场区连续三个月错配率上升？结合管理规范解释可能原因。”——后续 Metrics/SQL + RAG 复合路径，事实与推测分离。

安全负例：

1. `DELETE FROM dwd_breeding_event`——写操作必须拒绝。
2. “查询 payroll_employee 表中所有员工工资”——未授权表必须拒绝；Day 5～6 由 AST 与对象白名单验证。

## `dwd_breeding_event` 最小结构

| 字段 | 类型 | 作用 |
| --- | --- | --- |
| `event_id` | TEXT | 事件主键 |
| `event_date` | TEXT/DATE | 业务日期 |
| `farm_id` | TEXT | 场区维度 |
| `sow_line_id` | TEXT | 母系品系 |
| `boar_line_id` | TEXT | 公系品系 |
| `status` | valid/invalid | 是否计入有效配种分母 |
| `is_rule_match` | boolean | 是否符合模拟配种规则 |

Day 1 为了最小闭环直接保存 `is_rule_match`。Day 2～3 再决定是否引入带生效期的规则维表，避免首步就扩大 JOIN 和时态规则范围。

## 调用流程

```text
scripts/run_demo.py
  -> initialize_demo_database（仅首次或 --reset）
  -> answer_question
  -> route_question
      -> knowledge: lookup_metric_definition
      -> metrics: query_mismatch_rate -> execute_read_only
      -> blocked / clarify: 不访问数据库
  -> AgentResponse JSON
```

## Day 1～3 执行计划

1. Day 1：完成当前 CLI 纵向切片、合成数据、指标口径、成功/拒绝测试。
2. Day 2：建立项目虚拟环境；接入 FastAPI 与请求模型；将同一服务暴露为 `/v1/query`，不重写核心逻辑。
3. Day 2～3：Docker 可用后迁移 PostgreSQL；建立初始化脚本与只读查询账号；完成一个 API 级端到端集成测试。
4. Day 3：补最小 Streamlit 页面或先用 Swagger 演示，展示问题、route、SQL、参数、结果和限制。

最早演示路径不是等待所有框架完成，而是复用同一个 `answer_question` 核心：CLI 已跑通后，FastAPI 只是传输层，PostgreSQL 是数据库适配层。

