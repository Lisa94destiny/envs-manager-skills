---
name: envs-manager
description: >
  管理 Claude Code 的 API 模型配置与切换工具（envs）。以下情况自动触发本 skill：
  (1) 用户提到新 API 或 API Key 时，如"我买了 kimi 的 key"、"帮我添加 xxx"、"我有一个 xxx 的 API"、用户直接粘贴 API Key；
  (2) 用户想切换模型时，如"切换到 kimi"、"下次用 qwen"、"换成 deepseek"、"用 xxx 模型"、"切回官方 claude"；
  (3) 用户查询当前模型或已配置列表时，如"我现在用的是哪个模型"、"查看配置"；
  (4) 用户询问 envs 工具的安装或使用方法时。
---

# envs — Claude Code 模型环境管理器

**工具脚本**：`scripts/envs.py`（随 skill 打包，无需独立安装即可调用）
**配置文件**：`~/.claude-code-env.json`

调用方式（始终使用绝对路径）：
```bash
python3 <SKILL_BASE_DIR>/scripts/envs.py <命令> [参数]
```

---

## 每次触发后的第一步：确认 shell 集成

先静默运行 setup，它内部会自动检测是否已安装，跳过已安装的情况：

```bash
python3 <SKILL_BASE_DIR>/scripts/envs.py setup <SKILL_BASE_DIR>/scripts/envs.py
```

- 若输出含"已安装过，跳过"→ 无需处理，继续主流程。
- 若成功写入配置文件 → 告知用户：

  > 已完成终端集成安装（自动识别你的 shell 类型）。**请开一个新终端**，`envs` 命令就可以直接使用了。

setup 支持 zsh / bash / fish / PowerShell，自动检测，无需用户指定。

---

## API Key 安全说明

**API Key 绝不能出现在对话中。** 本工具使用系统密钥库存储 Key（macOS Keychain / Linux SecretService / Windows Credential Manager），对话记录中永远不会有明文 Key。

当用户提到购买了 API 时，**立即发出提醒**：

> ⚠️ 安全提示：请**不要**把 API Key 发在对话框里，防止 Key 泄露到日志中。
>
> 请先提供以下信息帮我完成配置（不含 Key）：
> 1. 官方文档链接 或 文档内容
> 2. 平台提供的 `ANTHROPIC_BASE_URL` 和 `ANTHROPIC_MODEL` 配置值（如有）
>
> 配置完成后，系统会引导你**在终端直接输入 Key**（不经过对话），安全存入系统密钥库。

---

## 主流程一：添加新 API 配置

### 触发词示例
"我买了 xxx 的 API"、"帮我加 xxx 模型"、"我有一个 xxx 的 API Key"。

### Step 1：确认 provider 信息

**前提确认**：不是所有 API Key 都能用于 Claude Code。只有实现了 Anthropic API 格式的套餐才兼容（不是通用的 OpenAI 格式）。

按以下顺序查找 `ANTHROPIC_BASE_URL` 和模型 ID：

**① 先查 `references/providers.md`**，按 provider 和套餐名称匹配。

**② 若未收录，优先让用户提供文档**（更准确）：

> 请提供以下任意一项：
> 1. 官方文档链接（最直接）
> 2. 文档中的 `ANTHROPIC_BASE_URL` 和 `ANTHROPIC_MODEL` 值
> 3. 平台的配置示例（如 `{"env": {"ANTHROPIC_BASE_URL": "..."}}` 格式）

**③ 用户不知道时，用 WebSearch 自己搜索**：
- 查询：`<provider名> Claude Code 支持` 或 `<provider名> Anthropic API 兼容`
- 从官方文档提取端点和模型 ID，不确定时告知用户搜索结果

**不要猜测**——同一家厂商的不同套餐端点可能完全不同（如百炼通用 vs Coding Plan）。

### Step 2：导入配置（不含 Key）

```bash
python3 <SKILL_BASE_DIR>/scripts/envs.py import --json '{
  "name": "简短别名（小写，如 kimi、qwen、deepseek）",
  "ANTHROPIC_BASE_URL": "确认好的 base URL",
  "ANTHROPIC_MODEL": "模型 ID",
  "description": "简短备注"
}'
```

同一 provider 多个配置时加后缀区分：`qwen-pro`、`qwen-fast`。

### Step 3：引导用户在终端输入 Key

```bash
python3 <SKILL_BASE_DIR>/scripts/envs.py setkey <名称>
```

此命令会在**终端**弹出 `API Key（不显示输入）：` 提示，用户直接粘贴，Key 直接写入系统密钥库，不经过对话，不留记录。

告知用户：
> 请在**终端**（不是这里）执行：`envs setkey <名称>`，然后粘贴你的 API Key，按回车确认。

### Step 4：设为默认模型

```bash
python3 <SKILL_BASE_DIR>/scripts/envs.py use <名称>
```

这一步把 `currentModel` 写入配置文件，下次开终端自动生效。

### Step 5：告知用户切换方式

> ✓ 配置完成，已设为默认模型。
>
> **下次打开新终端时自动生效**，直接运行 `claude` 就是 xxx 了，无需任何操作。
>
> **如果想在当前终端立刻切换**：退出 Claude Code（Ctrl+C 或输入 `exit`），
> 在终端运行 `envs use <名称>`，然后重新运行 `claude`。

---

## 主流程二：切换已有模型

### 触发词示例
"切换到 kimi"、"下次用 qwen"、"换成 deepseek"、"用 xxx"、"切回官方 claude"。

### Step 1：确认模型已配置

```bash
python3 <SKILL_BASE_DIR>/scripts/envs.py list
```

若目标模型不在列表中 → 走**主流程一**先添加配置。

### Step 2：更新默认模型

```bash
python3 <SKILL_BASE_DIR>/scripts/envs.py use <名称>
```

更新 `currentModel`，持久保存。

### Step 3：告知用户

> ✓ 已切换，下次打开新终端自动使用 xxx。
>
> **立刻生效**：退出当前 Claude Code → 终端运行 `envs use <名称>` → 重新运行 `claude`。

---

## 主流程三：查看当前状态

用户问"我现在用的哪个模型"、"列出所有配置"等：

```bash
python3 <SKILL_BASE_DIR>/scripts/envs.py list    # 所有配置及当前默认
python3 <SKILL_BASE_DIR>/scripts/envs.py status  # 当前终端实际生效的环境变量
```

---

## 关于切换的底层原理（用于解释给用户）

Claude Code 在**启动时**读取环境变量（`ANTHROPIC_BASE_URL`、`ANTHROPIC_AUTH_TOKEN`、`ANTHROPIC_MODEL`）并连接 API。运行中无法切换，因为不能更改自身的连接。

- `envs use <名称>` 做两件事：① 更新 `~/.claude-code-env.json`；② 在当前终端 `export` 对应变量
- 新终端启动时，autoload 函数读取配置文件，自动 `export` 变量，直接运行 `claude` 即用新模型
- 类比 `nvm use 18`：先切换版本，再运行程序，程序就用那个版本

---

## 关于 login 模式（切回官方 Claude 账号）

官方登录凭据存在 `~/.claude/`，与环境变量无关。只需：
- 提前 `claude login` 一次（凭据永久保存）
- 切回时：`envs use login`（unset 所有 API 环境变量，Claude Code 自动回落到本地凭据）
- **不需要重新 `claude login`**，也不需要 `claude logout`

"login" 配置不含 ANTHROPIC_AUTH_TOKEN，导入示例：
```json
{"name": "login", "description": "官方 Claude Code 登录模式"}
```

---

## 删除配置

```bash
python3 <SKILL_BASE_DIR>/scripts/envs.py remove <名称>
```

---

## Provider 参考

详见 `references/providers.md`，包含已验证的 provider 列表（base URL、模型 ID、注意事项）。
未收录的 provider：优先请用户提供文档，其次 WebSearch 查询，最后才让用户手动填写。
