# Claude Code 兼容 Provider 配置参考

> **核心前提**：Claude Code 使用 Anthropic API 格式，**不是** OpenAI 格式。
> 以下列出的都是**专门实现了 Anthropic API 兼容层**、可直接接入 Claude Code 的平台。
> 各家厂商的普通 API Key（OpenAI 格式）通常**不能直接使用**。

---

## 验证状态说明

- **[已验证]** — 经用户实际使用确认可用，或来自官方文档且有明确配置示例
- **[文档确认]** — 来自官方文档，但尚未经用户实际验证
- **[未验证]** — 来自第三方博客/搜索结果，模型名称/URL 可能已过时，**使用前必须请用户提供官方文档确认**

---

## Provider 列表

### 阿里云百炼 — Coding Plan `[已验证]`

> 官方专为 Claude Code 开设的套餐，**与普通百炼 API 端点完全不同**。
> 官方文档参考用户提供的配置示例（已实测）。

| ANTHROPIC_BASE_URL | ANTHROPIC_MODEL |
|---|---|
| `https://coding.dashscope.aliyuncs.com/apps/anthropic` | `qwen3.5-plus` |

> **⚠ 兼容性说明**：Claude Code 近期版本默认发送 `thinking: {type: "adaptive"}`，但此端点仅支持 `"enabled"` / `"disabled"`，会导致 `400 adaptive is not supported` 报错。
> 需设置 `CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING=1`，让 Claude Code 改用 `"enabled"` 模式。
>
> 若该变量不在管理列表中，先在终端运行：`envs env add CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING`

```json
{"name":"qwen-coder","ANTHROPIC_BASE_URL":"https://coding.dashscope.aliyuncs.com/apps/anthropic","ANTHROPIC_AUTH_TOKEN":"sk-xxx","ANTHROPIC_MODEL":"qwen3.5-plus","CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING":"1","description":"阿里百炼 Coding Plan"}
```

---

### 硅基流动 SiliconFlow — 聚合平台 `[文档确认]`

> 支持多家模型，一个 Key 可切换多个模型。
> 官方文档：https://docs.siliconflow.cn/cn/usercases/use-siliconcloud-in-ClaudeCode

| ANTHROPIC_BASE_URL | 说明 |
|---|---|
| `https://api.siliconflow.cn/` | 尾部斜杠不能省略 |

**常用模型 ID（可能随时更新，配置前以官方为准）：**
```
moonshotai/Kimi-K2-Instruct-0905
Qwen/Qwen3-Coder-480B-A35B-Instruct
deepseek-ai/DeepSeek-V3
THUDM/GLM-4.5
```

```json
{"name":"kimi-sf","ANTHROPIC_BASE_URL":"https://api.siliconflow.cn/","ANTHROPIC_AUTH_TOKEN":"sk-xxx","ANTHROPIC_MODEL":"moonshotai/Kimi-K2-Instruct-0905","description":"Kimi K2 via SiliconFlow"}
```

---

### DeepSeek 官方 `[文档确认]`

> 官方提供独立的 Anthropic 兼容端点（路径与普通 OpenAI 兼容端点不同）。
> 官方文档：https://api-docs.deepseek.com/guides/anthropic_api

| ANTHROPIC_BASE_URL | ANTHROPIC_MODEL |
|---|---|
| `https://api.deepseek.com/anthropic` | `deepseek-chat`（V3）/ `deepseek-reasoner`（R1） |

**官方建议同时设置：**`API_TIMEOUT_MS=600000` 和 `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1`

```json
{"name":"deepseek","ANTHROPIC_BASE_URL":"https://api.deepseek.com/anthropic","ANTHROPIC_AUTH_TOKEN":"sk-xxx","ANTHROPIC_MODEL":"deepseek-chat","description":"DeepSeek V3 官方"}
```

---

### 月之暗面 Kimi — 直连 `[未验证]`

> URL 来自官方文档页面，但模型名称从第三方博客提取，**可能已更新**。
> 官方文档：https://platform.moonshot.ai/docs/guide/agent-support（需在浏览器中打开查看最新模型 ID）

| ANTHROPIC_BASE_URL | ANTHROPIC_MODEL（参考，请以官方为准） |
|---|---|
| `https://api.moonshot.cn/anthropic/` | `kimi-k2-0905-preview`（未经实测） |

**⚠ 使用前请用户确认**：从官方文档获取当前有效的模型 ID 和 base URL。

```json
{"name":"kimi","ANTHROPIC_BASE_URL":"https://api.moonshot.cn/anthropic/","ANTHROPIC_AUTH_TOKEN":"sk-xxx","ANTHROPIC_MODEL":"kimi-k2-0905-preview","description":"Kimi K2 直连（模型名待确认）"}
```

---

### 智谱 GLM `[文档确认]`

> 官方提供 Claude API 兼容层，文档明确。
> 官方文档：https://docs.bigmodel.cn/cn/guide/develop/claude/introduction

| ANTHROPIC_BASE_URL | ANTHROPIC_MODEL |
|---|---|
| `https://open.bigmodel.cn/api/anthropic` | `glm-4.7`（旗舰）/ `glm-4.5-air`（性价比）/ `glm-4.5-flash`（免费） |

```json
{"name":"glm","ANTHROPIC_BASE_URL":"https://open.bigmodel.cn/api/anthropic","ANTHROPIC_AUTH_TOKEN":"sk-xxx","ANTHROPIC_MODEL":"glm-4.7","description":"智谱 GLM-4.7"}
```

---

### 火山引擎 — Coding Plan（字节跳动豆包）`[文档确认]`

> 需购买 Coding Plan 套餐，端点与普通火山引擎 API 不同。
> 官方文档：https://www.volcengine.com/docs/82379/1928262

| ANTHROPIC_BASE_URL | ANTHROPIC_MODEL |
|---|---|
| `https://ark.cn-beijing.volces.com/api/coding` | `doubao-seed-code-preview-latest` |

**官方建议同时设置：**`API_TIMEOUT_MS=3000000` 和 `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1`

```json
{"name":"doubao-coder","ANTHROPIC_BASE_URL":"https://ark.cn-beijing.volces.com/api/coding","ANTHROPIC_AUTH_TOKEN":"sk-xxx","ANTHROPIC_MODEL":"doubao-seed-code-preview-latest","description":"火山引擎豆包 Coding Plan"}
```

---

### OpenRouter — 国际聚合平台 `[文档确认]`

> 可路由到 Claude 原版及其他多家模型。
> 官方文档：https://openrouter.ai/docs/guides/guides/claude-code-integration

| ANTHROPIC_BASE_URL | ANTHROPIC_MODEL |
|---|---|
| `https://openrouter.ai/api` | 任意 OpenRouter 模型 ID（如 `anthropic/claude-sonnet-4-5`） |

**⚠ 特别注意**：必须将 `ANTHROPIC_API_KEY` 设为空字符串 `""`，否则报认证错误。

```json
{"name":"openrouter","ANTHROPIC_BASE_URL":"https://openrouter.ai/api","ANTHROPIC_AUTH_TOKEN":"sk-or-xxx","ANTHROPIC_MODEL":"anthropic/claude-sonnet-4-5","description":"OpenRouter 聚合"}
```

---

## login 模式（切回官方 Claude 账号）

```json
{"name":"login","description":"官方 Claude Code 登录模式，unset 所有 API 环境变量"}
```

---

## 处理未知 Provider 的规则

当用户提到的 provider **不在上方列表中**，或列表中该条目标注为 `[未验证]` 时：

**必须请用户提供以下任意一项**，不得猜测：

1. **官方文档链接** — 最佳选项，可自行提取配置
2. **文档中的配置片段** — 包含 `ANTHROPIC_BASE_URL`、`ANTHROPIC_MODEL` 的说明
3. **官方提供的环境变量配置示例**，例如：
   ```json
   {"env": {"ANTHROPIC_BASE_URL": "...", "ANTHROPIC_MODEL": "..."}}
   ```

获取后，将验证通过的配置更新到本文件对应条目，并将状态从 `[未验证]` 改为 `[已验证]` 或 `[文档确认]`。
