# 新手导览：这个项目的文件夹在做什么

## 1. 现在算不算前后端项目

现在还不是完整的前后端项目，更准确地说，它是一个已经能运行的“后端核心 + 命令行入口”。

- `scripts/run_demo.py` 接收你输入的问题，临时承担“入口”的角色。
- `app/` 处理路由、查数据和组织答案，是项目核心，接近以后后端内部的业务逻辑。
- Day 2 加入 FastAPI 后，浏览器或界面可以通过 HTTP 调用它，这才形成后端接口。
- 后续加入 Streamlit 后，才会出现按钮、输入框、表格和图表；它承担轻量前端/演示界面的角色。

不需要先学完整套前端开发。Streamlit 会直接用 Python 写界面，不要求先掌握 HTML、CSS、JavaScript 或 React。

## 2. 把项目想象成一家小餐厅

```text
用户问题                 点单
scripts/run_demo.py      服务员接单
app/router.py            判断送到哪个工作台
app/tools.py             按指标口径计算
app/database.py          去仓库取数据
data/                    仓库里的合成数据和业务说明
app/service.py           把各步骤串起来并组织答案
tests/                   质检员，检查结果有没有做错
docs/                    项目说明书和学习笔记
```

## 3. 顶层目录

### `app/`：真正工作的代码

- `models.py`：规定返回结果包含哪些字段，例如状态、路线、答案、SQL、引用。
- `router.py`：判断问题应该查指标、查知识、要求澄清，还是安全拒绝。
- `tools.py`：包含错配率 SQL 和指标定义检索工具。
- `database.py`：创建演示数据库，并用只读方式执行查询。
- `service.py`：总调度员，把路由和各工具连接起来。

### `data/`：项目使用的数据

- `synthetic/`：完全虚构的合成配种事件，不含真实公司数据。
- `knowledge/`：模拟指标定义和业务规则。
- `runtime/`：运行时生成的 SQLite 数据库；它被 Git 忽略，不上传。

### `scripts/`：给人使用的入口

- `run_demo.py`：输入一句自然语言问题，输出完整 JSON 结果。

### `tests/`：自动检查代码

- `test_vertical_slice.py`：检查指标结果、知识引用、安全拒绝和歧义澄清。
- 测试通过不等于整个项目完成，只证明当前四项行为符合预期。

### `docs/`：设计与学习资料

- `day1_minimum_vertical_slice.md`：Day 1 设计、环境和调用流程。
- `decisions/`：记录“为什么这样选”的架构决策。
- `learning_cards/`：阶段学习卡片和面试追问。

## 4. 顶层文件

- `README.md`：GitHub 首页说明和最常用运行方式。
- `pyproject.toml`：Python 版本和未来依赖范围，相当于项目配置清单。
- `.gitignore`：告诉 Git 哪些临时文件、数据库和密钥不能上传。
- `.env.example`：环境变量示例，只放字段名，绝不放真实 API Key。
- `AGENTS.md`：给 AI 开发助手看的项目执行规则。
- `task_state.md`：本地开发进度和下一步恢复点。
- `pitfall_log.md`：已经遇到的问题及可复用解决方法。
- `智能问数 Agent｜项目交接与 Codex 执行说明.md`：范围、路线和验收标准的总依据。

## 5. 你亲自运行

打开项目目录 `D:\Projects\智能问数agent`，在资源管理器地址栏输入 `powershell` 并回车。

本机 Python 没有加入 PATH，因此先使用已经找到的 Python 3.13：

```powershell
& "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe" -X utf8 -m unittest discover -s tests -v
```

看到 `Ran 4 tests` 和 `OK`，表示四个当前测试通过。然后运行指标问题：

```powershell
& "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe" -X utf8 scripts/run_demo.py --reset "2026年9月A场的错配率是多少，比8月提高了多少个百分点？"
```

重点观察输出中的五项：

1. `route` 是否为 `metrics`；
2. `answer` 是否显示 40% 和提高 15 个百分点；
3. `sql` 是否只包含查询；
4. `sql_parameters` 是否是 A、2026-08、2026-09；
5. `warnings` 是否说明当前使用受控 SQL，而不是 LLM 自由生成。

再试一个安全负例：

```powershell
& "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe" -X utf8 scripts/run_demo.py "DELETE FROM dwd_breeding_event"
```

预期 `status` 和 `route` 都是 `blocked`。

## 6. 现在只需要理解的调用顺序

```text
run_demo.py
  -> service.answer_question
  -> router.route_question
  -> tools.query_mismatch_rate
  -> database.execute_read_only
  -> AgentResponse JSON
```

第一次学习时按这个顺序打开文件即可，不需要从所有文件的第一行开始读。

