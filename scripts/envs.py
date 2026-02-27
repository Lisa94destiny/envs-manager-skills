#!/usr/bin/env python3
"""
envs - Claude Code 环境变量管理器
管理 Claude Code 的环境变量，轻松切换不同模型配置
"""

import json
import os
import platform
import sys
from pathlib import Path

CONFIG_FILE = Path.home() / ".claude-code-env.json"

# ANSI 颜色
RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
GREEN  = "\033[32m"
YELLOW = "\033[33m"
RED    = "\033[31m"
CYAN   = "\033[36m"

DEFAULT_ENV_VARS = [
    {"key": "ANTHROPIC_BASE_URL",   "required": True},
    {"key": "ANTHROPIC_AUTH_TOKEN", "required": True},
    {"key": "ANTHROPIC_MODEL",      "required": False},
    {"key": "ANTHROPIC_MAX_TOKENS", "required": False},
]

DEFAULT_CONFIG = {
    "models": [],
    "currentModel": None,
    "envVars": DEFAULT_ENV_VARS,
}

IMPORT_TEMPLATE = {
    "name": "模型别名（如 kimi、qwen、glm）",
    "ANTHROPIC_BASE_URL": "API 的 base URL（如 https://api.siliconflow.cn/v1）",
    "ANTHROPIC_AUTH_TOKEN": "你的 API Key",
    "ANTHROPIC_MODEL": "模型 ID（可选，如 moonshotai/Kimi-K2-Instruct）",
    "description": "备注（可选）"
}


# ── 配置读写 ──────────────────────────────────────────────────────────────────

def load_config() -> dict:
    if not CONFIG_FILE.exists():
        save_config(DEFAULT_CONFIG.copy())
        return DEFAULT_CONFIG.copy()
    with open(CONFIG_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_config(config: dict) -> None:
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def find_model(config: dict, name: str) -> dict | None:
    for m in config.get("models", []):
        if m["name"] == name:
            return m
    return None


# ── Shell 检测 ────────────────────────────────────────────────────────────────

def detect_shell() -> tuple[str, Path]:
    """返回 (shell 类型, 配置文件路径)"""
    system = platform.system()

    if system == "Windows":
        profile = Path.home() / "Documents" / "PowerShell" / "Microsoft.PowerShell_profile.ps1"
        return "powershell", profile

    shell_env = os.environ.get("SHELL", "")
    if "zsh" in shell_env:
        return "zsh", Path.home() / ".zshrc"
    elif "fish" in shell_env:
        return "fish", Path.home() / ".config" / "fish" / "config.fish"
    else:
        # bash fallback
        bashrc = Path.home() / ".bashrc"
        bash_profile = Path.home() / ".bash_profile"
        return "bash", bashrc if bashrc.exists() else bash_profile


def _shell_function_content(shell: str, envs_py_path: str) -> str:
    """生成对应 shell 的 envs() 函数内容"""
    p = envs_py_path.replace("'", "\\'")  # escape single quotes

    if shell in ("zsh", "bash"):
        return f"""
# envs - Claude Code Env Manager
envs() {{
    if [[ "$1" == "use" ]]; then
        local _cmds
        _cmds="$(python3 '{p}' --shell "$@" 2>/dev/null)"
        local _exit=$?
        if [[ $_exit -ne 0 ]]; then
            python3 '{p}' --shell "$@"
            return $_exit
        fi
        eval "$_cmds"
        echo "  \\033[32m✓ 已切换，当前终端环境变量已更新\\033[0m"
    else
        python3 '{p}' "$@"
    fi
}}
_envs_autoload() {{
    local _cmds
    _cmds="$(python3 '{p}' --autoload 2>/dev/null)"
    [[ $? -eq 0 && -n "$_cmds" ]] && eval "$_cmds"
}}
_envs_autoload
"""

    elif shell == "fish":
        return f"""
# envs - Claude Code Env Manager
function envs
    if test "$argv[1]" = "use"
        python3 '{p}' --shell $argv | source
        echo "  ✓ 已切换，当前终端环境变量已更新"
    else
        python3 '{p}' $argv
    end
end
function _envs_autoload
    set _cmds (python3 '{p}' --autoload 2>/dev/null)
    if test $status -eq 0 -a -n "$_cmds"
        echo $_cmds | source
    end
end
_envs_autoload
"""

    elif shell == "powershell":
        return f"""
# envs - Claude Code Env Manager
function envs {{
    if ($args[0] -eq 'use') {{
        $cmds = python3 '{p}' --shell @args 2>$null
        if ($LASTEXITCODE -eq 0) {{
            $cmds | Invoke-Expression
            Write-Host "  ✓ 已切换，当前终端环境变量已更新" -ForegroundColor Green
        }} else {{
            python3 '{p}' --shell @args
        }}
    }} else {{
        python3 '{p}' @args
    }}
}}
function _envs_autoload {{
    $cmds = python3 '{p}' --autoload 2>$null
    if ($LASTEXITCODE -eq 0 -and $cmds) {{ $cmds | Invoke-Expression }}
}}
_envs_autoload
"""
    return ""


# ── 命令实现 ──────────────────────────────────────────────────────────────────

def cmd_setup(envs_py_path: str | None = None) -> None:
    """自动检测 shell 并写入终端集成配置"""
    shell, config_file = detect_shell()
    marker = "# envs - Claude Code Env Manager"

    # 使用传入路径，或者默认用本文件自身的路径
    py_path = envs_py_path or str(Path(__file__).resolve())

    print(f"\n{BOLD}■ envs 终端集成安装{RESET}")
    print(f"  检测到: {shell}  →  {config_file}\n")

    # 确保父目录存在（fish config 目录可能不存在）
    config_file.parent.mkdir(parents=True, exist_ok=True)

    # 检查是否已安装
    if config_file.exists() and marker in config_file.read_text(encoding="utf-8"):
        existing = config_file.read_text(encoding="utf-8")
        # 提取当前嵌入的脚本路径，检查是否有效
        import re as _re
        m = _re.search(r"python3 '([^']+)' --autoload", existing)
        embedded_path = m.group(1) if m else ""
        if embedded_path and Path(embedded_path).exists() and embedded_path == py_path:
            print(f"  {YELLOW}⚠ 已安装过，跳过（路径有效）{RESET}\n")
            return
        # 路径无效或需要更新 → 替换旧块
        new_block = _shell_function_content(shell, py_path).lstrip("\n")
        # 找到旧块起止位置并替换
        start = existing.find(marker)
        end_marker_str = "_envs_autoload\n"
        end_idx = existing.find(end_marker_str, start)
        if end_idx != -1:
            end_idx += len(end_marker_str)
            updated = existing[:start] + new_block + existing[end_idx:]
        else:
            # 找不到结束标记，追加
            updated = existing + new_block
        with open(config_file, "w", encoding="utf-8") as f:
            f.write(updated)
        print(f"  {GREEN}✓ 已更新脚本路径 → {py_path}{RESET}")
        print(f"\n  {BOLD}请开一个新终端，之后直接用 envs 命令即可。{RESET}\n")
        return

    content = _shell_function_content(shell, py_path)
    with open(config_file, "a", encoding="utf-8") as f:
        f.write(content)

    print(f"  {GREEN}✓ 已写入 {config_file}{RESET}")
    print(f"\n  {BOLD}请开一个新终端，之后直接用 envs 命令即可。{RESET}\n")


def cmd_add(config: dict) -> None:
    print(f"\n{BOLD}■ 添加新模型配置{RESET}\n")

    name = input("  模型名称（如 kimi、qwen、claude）: ").strip()
    if not name:
        print(f"{RED}错误：名称不能为空{RESET}")
        return

    if find_model(config, name):
        print(f"{RED}错误：模型 '{name}' 已存在，请用 'envs remove {name}' 先删除{RESET}")
        return

    model: dict = {"name": name}
    env_vars = config.get("envVars", DEFAULT_ENV_VARS)

    for var in env_vars:
        key = var["key"]
        required = var.get("required", False)
        hint = "(必填)" if required else "(可选，直接回车跳过)"
        value = input(f"  {key} {hint}: ").strip()
        if value:
            model[key] = value
        elif required:
            print(f"  {YELLOW}⚠ {key} 未填写，切换到此模型时该变量将被 unset{RESET}")

    desc = input("  描述（可选）: ").strip()
    if desc:
        model["description"] = desc

    config["models"].append(model)
    save_config(config)
    print(f"\n{GREEN}✓ 模型 '{name}' 添加成功{RESET}\n")


def cmd_use(config: dict, name: str | None, shell_mode: bool = False) -> None:
    if not name:
        _err("请指定模型名称，例如: envs use kimi")
        sys.exit(1)

    model = find_model(config, name)
    if model is None:
        _err(f"模型 '{name}' 不存在，用 'envs list' 查看已配置的模型")
        sys.exit(1)

    config["currentModel"] = name
    save_config(config)

    env_vars = config.get("envVars", DEFAULT_ENV_VARS)

    if shell_mode:
        for var in env_vars:
            key = var["key"]
            value = model.get(key, "")
            if value:
                escaped = value.replace("'", "'\\''")
                print(f"export {key}='{escaped}'")
            else:
                print(f"unset {key} 2>/dev/null; true")
    else:
        print(f"\n{GREEN}✓ 已切换到 '{name}'{RESET}")
        print(f"  {DIM}开一个新终端即可生效{RESET}\n")


def cmd_list(config: dict) -> None:
    models = config.get("models", [])
    current = config.get("currentModel")

    print(f"\n{BOLD}■ 已配置的模型{RESET}\n")

    if not models:
        print(f"  {DIM}暂无配置。运行 'envs add' 添加第一个模型。{RESET}\n")
        return

    name_w = max(len(m["name"]) for m in models)
    name_w = max(name_w, 8) + 2
    model_w = 35

    print(f"  {DIM}{'─' * (name_w + model_w + 20)}{RESET}")
    print(f"  {BOLD}{'NAME':<{name_w}} {'ANTHROPIC_MODEL':<{model_w}} 描述{RESET}")
    print(f"  {DIM}{'─' * (name_w + model_w + 20)}{RESET}")

    for m in models:
        name = m["name"]
        model_str = m.get("ANTHROPIC_MODEL", "Default")
        desc = m.get("description", "")
        marker = f"{GREEN}●{RESET}" if name == current else " "
        print(f"{marker} {name:<{name_w}} {model_str:<{model_w}} {DIM}{desc}{RESET}")

    print(f"\n  当前模型: {BOLD}{current or '(未选择)'}{RESET}\n")


def cmd_status(config: dict) -> None:
    print(f"\n{BOLD}■ 当前状态{RESET}\n")

    current_name = config.get("currentModel")
    model = find_model(config, current_name) if current_name else None

    if model:
        desc = model.get("description", "")
        print(f"  当前模型:  {BOLD}{GREEN}{current_name}{RESET}" +
              (f"  {DIM}({desc}){RESET}" if desc else ""))
    else:
        print(f"  当前模型:  {DIM}(未选择){RESET}")

    print(f"\n  {BOLD}环境变量实际值:{RESET}")
    env_vars = config.get("envVars", DEFAULT_ENV_VARS)

    for var in env_vars:
        key = var["key"]
        actual = os.environ.get(key, "")
        if actual:
            display = actual if len(actual) <= 24 else actual[:10] + "..." + actual[-6:]
            print(f"  {GREEN}✓{RESET}  {key:<28} {DIM}={RESET} {display}")
        else:
            print(f"  {DIM}✗  {key:<28} (未设置){RESET}")

    print()


def cmd_remove(config: dict, name: str | None) -> None:
    if not name:
        _err("请指定模型名称，例如: envs remove kimi")
        return

    models = config.get("models", [])
    new_models = [m for m in models if m["name"] != name]

    if len(new_models) == len(models):
        _err(f"模型 '{name}' 不存在")
        return

    config["models"] = new_models
    if config.get("currentModel") == name:
        config["currentModel"] = None
    save_config(config)
    print(f"{GREEN}✓ 已删除模型 '{name}'{RESET}")


def cmd_template() -> None:
    print(f"""
{BOLD}■ envs 配置模板{RESET}

{DIM}将下面的内容连同你的 API 文档一起发给任意 AI，让它帮你填写：{RESET}

请根据下面的 JSON 格式和我提供的 API 文档，帮我填写配置。
只需返回填好的 JSON，不需要其他解释。

{CYAN}{json.dumps(IMPORT_TEMPLATE, indent=2, ensure_ascii=False)}{RESET}

{DIM}填好后，运行 'envs import' 并粘贴 AI 返回的 JSON 即可导入。{RESET}
""")


def cmd_import(config: dict, inline_json: str | None = None) -> None:
    if inline_json:
        raw = inline_json
    else:
        print(f"\n{BOLD}■ 导入模型配置{RESET}")
        print(f"  {DIM}粘贴 JSON（单个对象 {{...}} 或数组 [{{...}}]），完成后按 Ctrl+D：{RESET}\n")
        try:
            lines = []
            while True:
                try:
                    line = input()
                    lines.append(line)
                except EOFError:
                    break
            raw = "\n".join(lines)
        except KeyboardInterrupt:
            print(f"\n{DIM}已取消{RESET}")
            return

    if not raw.strip():
        _err("未收到任何输入")
        return

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        _err(f"JSON 格式有误：{e}")
        return

    models_to_import = data if isinstance(data, list) else [data]

    imported = 0
    skipped = 0
    for entry in models_to_import:
        if not isinstance(entry, dict):
            print(f"  {YELLOW}⚠ 跳过无效条目（非对象）{RESET}")
            skipped += 1
            continue

        name = entry.get("name", "").strip()
        if not name:
            print(f"  {YELLOW}⚠ 跳过缺少 'name' 字段的条目{RESET}")
            skipped += 1
            continue

        # 过滤掉模板占位文字
        model = {k: v for k, v in entry.items()
                 if not isinstance(v, str) or not any(
                     placeholder in v for placeholder in
                     ["模型别名", "API 的 base", "你的 API", "备注（可选）", "模型 ID（可选"]
                 )}

        existing = find_model(config, name)
        if existing:
            try:
                answer = input(f"  模型 '{name}' 已存在，覆盖？[y/N] ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                answer = "n"
            if answer != "y":
                print(f"  {DIM}已跳过 '{name}'{RESET}")
                skipped += 1
                continue
            config["models"] = [m for m in config["models"] if m["name"] != name]

        config["models"].append(model)
        print(f"  {GREEN}✓ 已导入 '{name}'{RESET}")
        imported += 1

    save_config(config)
    print(f"\n  完成：导入 {imported} 个，跳过 {skipped} 个\n")


def cmd_env(config: dict, args: list[str]) -> None:
    if not args:
        env_vars = config.get("envVars", DEFAULT_ENV_VARS)
        print(f"\n{BOLD}■ 环境变量{RESET}\n")
        for i, var in enumerate(env_vars, 1):
            req = f" {BOLD}(必填){RESET}" if var.get("required") else ""
            print(f"  {i}. {var['key']}{req}")
        print(f"\n  {DIM}命令:")
        print(f"  envs env add <KEY>    添加自定义环境变量")
        print(f"  envs env remove       删除非必填环境变量{RESET}\n")
        return

    subcmd = args[0]

    if subcmd == "add":
        if len(args) < 2:
            _err("用法: envs env add <KEY>")
            return
        key = args[1].upper()
        env_vars = config.get("envVars", DEFAULT_ENV_VARS)
        if any(v["key"] == key for v in env_vars):
            print(f"{YELLOW}变量 '{key}' 已存在{RESET}")
            return
        env_vars.append({"key": key, "required": False})
        config["envVars"] = env_vars
        save_config(config)
        print(f"{GREEN}✓ 已添加环境变量 '{key}'{RESET}")

    elif subcmd == "remove":
        env_vars = config.get("envVars", DEFAULT_ENV_VARS)
        removable = [v for v in env_vars if not v.get("required")]
        if not removable:
            print(f"{YELLOW}没有可删除的环境变量（必填变量不可删除）{RESET}")
            return
        print(f"\n{BOLD}选择要删除的变量:{RESET}")
        for i, var in enumerate(removable, 1):
            print(f"  {i}. {var['key']}")
        try:
            choice = int(input("\n  输入编号: ").strip())
            if 1 <= choice <= len(removable):
                key = removable[choice - 1]["key"]
                config["envVars"] = [v for v in env_vars if v["key"] != key]
                save_config(config)
                print(f"{GREEN}✓ 已删除 '{key}'{RESET}")
            else:
                _err("编号无效")
        except (ValueError, KeyboardInterrupt):
            print(f"\n{DIM}已取消{RESET}")
    else:
        _err(f"未知子命令: {subcmd}")


def cmd_help() -> None:
    print(f"""
{BOLD}envs - Claude Code 环境变量管理器{RESET}

{BOLD}用法:{RESET}
  envs <命令> [参数]

{BOLD}命令:{RESET}
  {GREEN}setup{RESET}            自动检测 shell 并安装终端集成（首次使用）
  {GREEN}add{RESET}              添加新的模型配置（交互式）
  {GREEN}use <名称>{RESET}       切换到指定模型
  {GREEN}list{RESET}             列出所有已配置的模型
  {GREEN}status{RESET}           查看当前环境变量的实际值
  {GREEN}remove <名称>{RESET}    删除一个模型配置
  {GREEN}template{RESET}         打印可发给 AI 的配置模板
  {GREEN}import{RESET}           粘贴 JSON 直接导入配置
  {GREEN}env{RESET}              查看/管理环境变量列表
  {GREEN}help{RESET}             显示此帮助

{BOLD}快速上手:{RESET}
  1. envs setup         # 首次安装终端集成（之后开新终端生效）
  2. 告诉 Claude 你的 API 信息，它会自动导入配置
  3. 开新终端，直接使用

{BOLD}提示:{RESET}
  配置保存在 {DIM}~/.claude-code-env.json{RESET}
  "登录模式"：不填 ANTHROPIC_AUTH_TOKEN 即可回落到 claude login 凭据
""")


# ── 工具函数 ──────────────────────────────────────────────────────────────────

def _err(msg: str) -> None:
    print(f"{RED}错误：{msg}{RESET}", file=sys.stderr)


# ── 入口 ──────────────────────────────────────────────────────────────────────

def main() -> None:
    args = sys.argv[1:]

    shell_mode = "--shell" in args
    if shell_mode:
        args.remove("--shell")

    inline_json = None
    if "--json" in args:
        idx = args.index("--json")
        if idx + 1 < len(args):
            inline_json = args[idx + 1]
            args = args[:idx] + args[idx + 2:]
        else:
            _err("--json 需要跟一个 JSON 字符串")
            sys.exit(1)

    # --autoload：新终端启动时静默应用当前模型
    if "--autoload" in args:
        config = load_config()
        current = config.get("currentModel")
        if current:
            model = find_model(config, current)
            if model:
                env_vars = config.get("envVars", DEFAULT_ENV_VARS)
                for var in env_vars:
                    key = var["key"]
                    value = model.get(key, "")
                    if value:
                        escaped = value.replace("'", "'\\''")
                        print(f"export {key}='{escaped}'")
                    else:
                        print(f"unset {key} 2>/dev/null; true")
        sys.exit(0)

    config = load_config()

    if not args:
        cmd_help()
        return

    cmd = args[0]

    if cmd == "setup":
        py_path = args[1] if len(args) > 1 else None
        cmd_setup(py_path)
    elif cmd == "add":
        cmd_add(config)
    elif cmd == "use":
        name = args[1] if len(args) > 1 else None
        cmd_use(config, name, shell_mode=shell_mode)
    elif cmd in ("list", "ls"):
        cmd_list(config)
    elif cmd == "status":
        cmd_status(config)
    elif cmd in ("remove", "rm"):
        name = args[1] if len(args) > 1 else None
        cmd_remove(config, name)
    elif cmd == "template":
        cmd_template()
    elif cmd == "import":
        cmd_import(config, inline_json=inline_json)
    elif cmd == "env":
        cmd_env(config, args[1:])
    elif cmd in ("help", "--help", "-h"):
        cmd_help()
    else:
        _err(f"未知命令: {cmd}")
        print(f"  运行 'envs help' 查看可用命令")
        sys.exit(1)


if __name__ == "__main__":
    main()
