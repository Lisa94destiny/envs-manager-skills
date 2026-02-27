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
envs setkey <名称>          # 更新某个模型的 API Key
envs status                # 查看当前终端实际生效的环境变量
envs remove <名称>          # 删除一个模型配置
envs help                  # 查看所有命令
```

## 支持的 Provider

详见 [references/providers.md](references/providers.md)，包含已验证可用于 Claude Code 的国内外主流服务商列表。

## 安全说明

API Key 存储在系统密钥库中，不出现在任何配置文件或对话记录里。通过 `envs setkey` 命令在终端直接输入（输入内容不显示），全程不经过 Claude。

## License

MIT
