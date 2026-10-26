# Windows 兼容性模拟冒烟测试记录（2026-10-26）

对工作流 E-0/E 的每个步骤按 Windows 环境推演（依据 ego-browser 官方 install.md 的 Windows 章节）：

| # | 步骤 | macOS 命令 | Windows 等价 | 推演结果 | 需要的动作 |
| --- | --- | --- | --- | --- | --- |
| 1 | 检测命令 | `command -v ego-browser` | `Get-Command ego-browser`（PS）/ `where ego-browser`（cmd） | ✅ 语法已内置 | 无 |
| 2 | 安装 | install.sh（DMG 自动装） | 无脚本，官网 https://lite.ego.app/ 下载安装包 | ✅ 工作流已分流 | SmartScreen 拦截→"更多信息→仍要运行" |
| 3 | PATH 注册 | onboarding 写入 ~/.local/bin | onboarding 注册 PATH，**只对新进程生效** | ⚠️ 已内置 | 装完必须"新开终端"再验证 |
| 4 | heredoc 传脚本 | `ego-browser nodejs <<'EOF'` | heredoc 不存在 | ⚠️ 需适配 | 单行用 `-e '...'`（双引号内层）；多行写 UTF-8 .mjs 文件再 `await import('file:///C:/.../task.mjs')`（正斜杠） |
| 5 | 非 ASCII 参数 | 直接传中文 | PowerShell 5.1 会把中文转 ANSI 乱码 | ⚠️ 已内置 | 中文/双引号一律放 .mjs 文件里，绝不放 -e 参数 |
| 6 | 文件路径 | /Volumes/... 绝对路径 | C:/Users/...（**正斜杠**，反斜杠是转义符） | ⚠️ 需适配 | setFiles 用正斜杠绝对路径 |
| 7 | 截图/产物路径 | /tmp/... | C:/Users/<name>/ego-shots/... | ✅ 同上 | 无 |
| 8 | 验证运行时 | `ego-browser nodejs <<'EOF' console.log('ready') EOF` | `ego-browser nodejs -e "console.log('ready')"` | ✅ 语法已内置 | 无 |

结论：Windows 下管家需要 4 处行为分流（3/4/5/6），已全部写入工作流 E-0 与本表。真正的 Windows 实机冒烟（在 Windows 机器上从安装到提交技能全流程）待有环境后补测，在此之前 Windows 用户的代上架按"引导+验证"模式进行，每步截图回报。
