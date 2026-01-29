import subprocess
import os
from mcp.server.fastmcp import FastMCP


class GitService:
    def __init__(self, workspace_root: str):
        # workspace_root 是你存放所有代码仓库的总目录（例如 /Users/fengyue/Projects）
        self.workspace_root = os.path.abspath(workspace_root)
        if not os.path.exists(self.workspace_root):
            os.makedirs(self.workspace_root)

    def register_tools(self, mcp: FastMCP):
        @mcp.tool(name="git_clone")
        async def git_clone(repo_url: str, folder_name: str) -> str:
            """
            克隆远程仓库到本地。
            :param repo_url: 仓库地址 (HTTPS 或 SSH)
            :param folder_name: 本地保存的文件夹名称
            """
            target_path = os.path.join(self.workspace_root, folder_name)
            if os.path.exists(target_path):
                return f"错误：目录 {folder_name} 已存在，无法克隆。"

            try:
                result = subprocess.run(
                    ["git", "clone", repo_url, folder_name],
                    cwd=self.workspace_root,
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    return f"成功克隆至 {target_path}:\n{result.stdout}"
                return f"克隆失败:\n{result.stderr}"
            except Exception as e:
                return f"异常: {str(e)}"

        @mcp.tool(name="git_manage")
        async def git_manage(repo_name: str, action: str, message: str = "", branch: str = "main") -> str:
            """
            对本地已存在的仓库执行 Git 操作 (status, pull, push, add, commit)。
            :param repo_name: 仓库文件夹名称
            :param action: 执行的动作 (status/pull/push/add/commit/log)
            """
            repo_path = os.path.join(self.workspace_root, repo_name)
            if not os.path.exists(repo_path):
                return f"错误：未找到仓库目录 {repo_name}，请先执行 clone。"

            commands = {
                "status": ["git", "status"],
                "pull": ["git", "pull", "origin", branch],
                "push": ["git", "push", "origin", branch],
                "add": ["git", "add", "."],
                "log": ["git", "log", "--oneline", "-n", "5"],
                "commit": ["git", "commit", "-m", message]
            }

            if action not in commands:
                return f"不支持的操作: {action}"

            try:
                result = subprocess.run(
                    commands[action],
                    cwd=repo_path,
                    capture_output=True,
                    text=True
                )
                output = result.stdout if result.returncode == 0 else result.stderr
                return f"[{action.upper()}] 结果:\n{output}"
            except Exception as e:
                return f"执行异常: {str(e)}"