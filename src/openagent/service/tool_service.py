import sys

from openagent.tool import file_tool
from openagent.tool import mcp_tool
from openagent.tool import shell_tool
from openagent.tool import skill_tool

POWERSHELL_DESCRIPTION = """
powershell -Command <command>                                   # Execute a command in PowerShell on Windows.
"""
BASH_DESCRIPTION = """
bash -c <command>                                               # Execute a command in Bash on Linux/macOS.
"""
DESCRIPTION = f"""
Execute a built-in command. Available commands:
file read <path>                                                # Read file content from <path>.
file write <path> <content>                                     # Write <content> to <path>. Creates the file if it doesn't exist, overwrites if it does.
file edit <path> <old_str> <new_str>                            # Replace all exact matches of <old_str> with <new_str> in <path>.
skill list                                                      # List all available skills.
mcp server list                                                 # List all MCP servers.
mcp server <server_name> tool list                              # List all tools of a specific MCP server.
mcp server <server_name> tool <tool_name> info                  # Show parameter format of a specific tool.
mcp server <server_name> tool <tool_name> call <tool_json_args> # Call a specific tool with JSON arguments.
{POWERSHELL_DESCRIPTION if sys.platform.startswith("win") else BASH_DESCRIPTION}
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


# 获取工具描述列表
def get_anthropic_tools() -> list[dict]:
    return [COMMAND_TOOL]


# 执行选择的工具
async def execute_tool(name: str, tool_input: dict, work_dir: str) -> tuple[str, bool]:
    try:
        if name != "command":
            return f"Unknown tool: {name}", True
        if not tool_input.get("args"):
            return "No args", True
        args: list[str] = tool_input["args"]
        if args[0] == "file":
            return await file_tool.execute(args, work_dir)
        if args[0] == "skill":
            return await skill_tool.execute(args, work_dir)
        if args[0] == "mcp":
            return await mcp_tool.execute(args, work_dir)
        return await shell_tool.execute(args, work_dir)
    except Exception as e:
        return f"{e}", True
