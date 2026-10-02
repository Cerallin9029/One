# Codex Instruction Lens

解释指定工作目录下 Codex 项目指令文件的选择、覆盖顺序和字节截断位置。
这是独立的只读本地工具，用 Python 3.11+ 标准库实现，没有运行时依赖或模型 API 调用。

## 安装和演示

在源码目录运行（仓库尚未公开时需要访问权限；目前未发布到 PyPI）：

```sh
python -m pip install .
codex-instruction-lens examples/monorepo/apps/api/src --root examples/monorepo
```

演示会选择仓库级 `AGENTS.md` 和 API 目录的 `AGENTS.override.md`，并解释
同目录的普通 `AGENTS.md` 为什么被遮蔽。

```sh
codex-instruction-lens . --json
codex-instruction-lens . --max-bytes 16384 --fallback-file TEAM.md
codex-instruction-lens . --show-text
codex-instruction-lens . --fail-on-warning
```

默认只输出路径、来源和字节计数；`--show-text` 才包含指令正文。
路径也可能包含个人信息，分享前应检查。终端中的正文采用 JSON 转义显示。

## 选择规则

1. 从工作目录向上寻找最近的 `.git` 标记，可为目录或 worktree 的文件。
2. 无标记时只检查工作目录；`--no-root-search` 可以明确禁用父目录搜索。
3. 从项目根目录到工作目录依次检查，每个目录只选一个文件。
4. 优先级：`AGENTS.override.md`、`AGENTS.md`、显式提供的 fallback 文件名。
5. 空覆盖文件仍会遮蔽普通文件，但空白内容不消耗有效项目内容预算。
6. 默认项目预算为 32,768 字节；超过预算会截断，后续文件显示为跳过。

`--root-marker NAME` 可重复使用，以替换默认根目录标记。
`--root PATH` 用于指定模拟边界；PATH 必须为工作目录本身或其祖先目录。
`--untrusted` 模拟跳过不受信任项目的指令。

退出码：完成为 0；启用 `--fail-on-warning` 且有警告时为 1；参数或文件错误为 2。

## 当前范围

初版只模拟单个本地环境的**项目文档**加载，并使用显式设置。
不读取 Codex 配置、账号指令或凭据，也不审计正在运行的会话。
全局指令、多层配置、多个环境、模型实际服从行为不在初版范围内。
工作目录会解析为物理路径，目录符号链接可能与上游路径处理不同。

行为以固定上游源码为参考；详见 [兼容性记录](COMPATIBILITY.md)。
开源建设安排见 [12 周计划](OSS_PLAN.zh-CN.md)。本项目与 OpenAI 无隶属或背书关系。
