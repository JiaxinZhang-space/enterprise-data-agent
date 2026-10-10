# 智能问数 Agent 踩坑日志

## 【2026-10-10】踩坑记录

- 问题场景：Windows 沙箱运行 SQLite 测试时先出现 `sqlite3.OperationalError: unable to open database file`；改到仓库临时目录后又出现 `[WinError 32] 另一个程序正在使用此文件`，导致测试清理失败。
- 排查过程：确认 CLI 在仓库 `data/runtime` 可正常建库；将 `tempfile` 根目录改到可写仓库；发现 `sqlite3.Connection` 的上下文管理器只管理事务，不保证关闭连接，Windows 因文件句柄未释放而拒绝删除测试库。
- 最终方案：测试使用 `TemporaryDirectory(dir=PROJECT_ROOT / "data/runtime/tests")`；应用和测试中的连接统一用 `contextlib.closing(sqlite3.connect(...))`，初始化写入后显式 `commit()`。
- 预防建议：Windows 上对文件型数据库做隔离测试时，临时目录必须位于确认可写位置；不要把 `with sqlite3.connect(...)` 误认为自动关闭连接；测试结束前显式释放所有数据库句柄。

