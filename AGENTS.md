# Project execution rules

- Treat `智能问数 Agent｜项目交接与 Codex 执行说明.md` as the scope authority.
- Keep the first release to one workflow with multiple tools. Do not add multi-agent orchestration.
- Use synthetic data only. Never copy real company schemas, data, code, or internal metric definitions.
- Never commit secrets. Model credentials must come from environment variables.
- Do not claim a feature, metric, deployment, or test result unless it was actually run and recorded.
- Every increment must include a success case, a failure or boundary case, tests, and a short learning card.
- Record current progress and decisions in `task_state.md` and `docs/decisions/`.
- Ask before paid services, destructive data operations, or major architecture changes.

## Local verification

Use a Python 3.11+ interpreter and run:

```powershell
python -m unittest discover -s tests -v
python scripts/run_demo.py --reset "2026年9月A场的错配率是多少，比8月提高了多少个百分点？"
```

