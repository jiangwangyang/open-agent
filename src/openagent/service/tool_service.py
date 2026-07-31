import sys

from openagent.tool import command_tool
from openagent.tool import file_tool
from openagent.tool import mcp_tool
from openagent.tool import skill_tool

DESCRIPTION = """
Execute a built-in command. Available commands:
file read <path>                                                # Read file content from <path>.
file write <path> <content>                                     # Write <content> to <path>. Creates the file if it doesn't exist, overwrites if it does.
file edit <path> <old_str> <new_str>                            # Replace all exact matches of <old_str> with <new_str> in <path>.
skill list                                                      # List all available skills.
mcp server list                                                 # List all MCP servers.
mcp server <server_name> tool list                              # List all tools of a specific MCP server.
mcp server <server_name> tool <tool_name> info                  # Show parameter format of a specific tool.
mcp server <server_name> tool <tool_name> call <tool_json_args> # Call a specific tool with JSON arguments.
"""
COMMAND_TOOL = {
    "name": "command",
    "description": DESCRIPTION,
    "input_schema": {
        "type": "object",
        "properties": {
            "args": {
                "type": "array",
                "description": "Command and its arguments as an array. The first element is the command name, followed by the corresponding arguments. Example: [\"file\", \"read\", \"/path/to/file.txt\"]",
                "items": {
                    "type": "string"
                }
            }
        },
        "required": ["args"]
    }
}
BASH_TOOL = {
    "name": "bash",
    "description": "Execute a command in Bash on Linux/macOS. Use ';' to run commands sequentially. Use '&&' to run the next command only if the previous succeeds.",
    "input_schema": {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "Bash command to execute.",
            }
        },
        "required": ["command"]
    }
}
POWERSHELL_TOOL = {
    "name": "powershell",
    "description": "Execute a command in PowerShell on Windows. Use ';' to run commands sequentially. Use '&&' to run the next command only if the previous succeeds.",
    "input_schema": {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "PowerShell command to execute.",
            }
        },
        "required": ["command"]
    }
}


# 获取工具描述列表
def get_anthropic_tools() -> list[dict]:
    return [COMMAND_TOOL, POWERSHELL_TOOL if sys.platform.startswith("win") else BASH_TOOL]


# 执行选择的工具
async def execute_tool(name: str, tool_input: dict, work_dir: str) -> tuple[str, bool]:
    try:
        # command
        if name == "command":
            if not tool_input.get("args"):
                return "No args", True
            args: list[str] = tool_input["args"]
            if args[0] == "file":
                return await file_tool.execute(args, work_dir)
            if args[0] == "skill":
                return await skill_tool.execute(args, work_dir)
            if args[0] == "mcp":
                return await mcp_tool.execute(args, work_dir)
            return f"Unknown command: {args[0]}", True
        # powershell bash
        if name == "powershell" or name == "bash":
            if not tool_input.get("command"):
                return "No command", True
            command: str = tool_input["command"]
            return await command_tool.execute(command, work_dir)
        # unknown
        return f"Unknown tool: {name}", True
    except Exception as e:
        return f"{e}", True
