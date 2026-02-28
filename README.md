# envs-manager-skills

一个 [Claude Code Skill](https://docs.anthropic.com/en/docs/claude-code/skills)，让你轻松管理多个大模型 API 配置，在不同模型之间一键切换。

## 功能

- 添加、切换、删除多个模型配置（阿里百炼、硅基流动、DeepSeek、智谱等）
- API Key 存入系统密钥库（macOS Keychain），不落盘、不进对话记录
- 新终端自动加载上次切换的模型，无需重复设置
- 支持 zsh / bash / fish / PowerShell

## 安装

在 Claude Code 中运行：

```
/skills install https://github.com/Lisa94destiny/envs-manager-skills
```

安装后，告诉 Claude："帮我配置 xxx 的 API"，skill 会自动引导完成后续步骤。

## 常用命令

安装完成后，终端可直接使用 `envs` 命令：

```bash
envs list                  # 查看所有配置及当前默认模型
envs use <名称>             # 切换模型（当前终端立即生效）
envs reset                 # 清除所有 API 环境变量，退回 /login 官方模式
envs setkey <名称>          # 更新某个模型的 API Key
envs status                # 查看当前终端实际生效的环境变量
envs remove <名称>          # 删除一个模型配置
envs help                  # 查看所有命令
```

## 支持的 Provider

详见 [references/providers.md](references/providers.md)，包含已验证可用于 Claude Code 的国内外主流服务商列表。

## 常见问题

### 报错 `400 adaptive is not supported`

Claude Code 近期版本默认开启 extended thinking，会发送 `thinking: {type: "adaptive", ...}`，但阿里百炼（DashScope）等部分端点仅支持 `"enabled"` / `"disabled"`，不接受 `"adaptive"`。

**解决方法**：设置 `CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING=1`，让 Claude Code 改用 `"enabled"` 模式（Qwen 支持）：

```bash
envs env add CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING   # 添加到管理列表（只需一次）
```

然后在 `envs add` 或 `envs import` 时，将该变量填为 `1`。配置示例见 [providers.md](references/providers.md) 对应章节。

### 报错 `403 invalid api-key / Please run /login`

`ANTHROPIC_AUTH_TOKEN` 未正确设置，Claude Code 回退使用 `/login` 存储的 Anthropic 凭据，发往第三方端点后被拒绝。

检查步骤：

1. 运行 `envs setkey <名称>` 重新输入并保存 API Key
2. 开新终端，运行 `envs status` 确认 `ANTHROPIC_AUTH_TOKEN` 已生效

### 第三方模型出问题时如何快速切回官方 Claude？

在任意终端运行：

```bash
envs reset
```

这会立即 unset 当前终端的所有 API 环境变量，并清除 autoload 的默认模型。之后直接运行 `claude`，它会使用 `/login` 存储的官方凭据。

恢复第三方模型时，再运行 `envs use <名称>` 即可。

### 临时 `export` 与 autoload 是否冲突？

不冲突。autoload 在终端启动时运行一次；之后在同一终端手动 `export` 会覆盖当前 session，不影响 `~/.claude-code-env.json` 中的默认配置，下个终端重新 autoload。

若临时测试**支持 adaptive thinking 的官方 Claude**，记得手动 `unset CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING`。

## 安全说明

API Key 存储在系统密钥库中，不出现在任何配置文件或对话记录里。通过 `envs setkey` 命令在终端直接输入（输入内容不显示），全程不经过 Claude。

## License

MIT
