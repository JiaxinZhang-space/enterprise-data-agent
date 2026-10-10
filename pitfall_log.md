# 智能问数 Agent 踩坑日志

## 【2026-10-10】踩坑记录

- 问题场景：Windows 沙箱运行 SQLite 测试时先出现 `sqlite3.OperationalError: unable to open database file`；改到仓库临时目录后又出现 `[WinError 32] 另一个程序正在使用此文件`，导致测试清理失败。
- 排查过程：确认 CLI 在仓库 `data/runtime` 可正常建库；将 `tempfile` 根目录改到可写仓库；发现 `sqlite3.Connection` 的上下文管理器只管理事务，不保证关闭连接，Windows 因文件句柄未释放而拒绝删除测试库。
- 最终方案：测试使用 `TemporaryDirectory(dir=PROJECT_ROOT / "data/runtime/tests")`；应用和测试中的连接统一用 `contextlib.closing(sqlite3.connect(...))`，初始化写入后显式 `commit()`。
- 预防建议：Windows 上对文件型数据库做隔离测试时，临时目录必须位于确认可写位置；不要把 `with sqlite3.connect(...)` 误认为自动关闭连接；测试结束前显式释放所有数据库句柄。

## 【2026-10-10】踩坑记录

- 问题场景：GitHub 公开仓库已创建，但首次 `git push` 报错 `Failed to connect to 127.0.0.1 port 7897`。
- 排查过程：检查远程地址正常；通过 `git config --show-origin` 确认全局 `http.proxy` 和 `https.proxy` 指向当前未运行的本地代理 `127.0.0.1:7897`；未删除用户全局配置。
- 最终方案：只对本次操作执行 `git -c http.proxy= -c https.proxy= push -u origin main`，推送成功后用 `git ls-remote --heads origin main` 对账远程提交。
- 预防建议：以后 Git 网络操作出现同一端口错误时，先核对代理来源；使用单命令临时绕过，避免擅自修改可能供其他场景使用的全局代理。

