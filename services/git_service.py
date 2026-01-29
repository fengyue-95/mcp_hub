import subprocess
import os
from mcp.server.fastmcp import FastMCP


class GitService:
    def __init__(self, default_workspace: str = "/Users/fengyue/PycharmProjects"):
        # 这里的路径仅作为默认值
        self.default_workspace = os.path.abspath(default_workspace)

    def register_tools(self, mcp: FastMCP):
        @mcp.tool(name="git_clone")
        async def git_clone(repo_url: str, folder_name: str, workspace_path: str = None) -> str:
            """
            克隆远程仓库到本地。
            :param repo_url: 仓库地址 (HTTPS 或 SSH)
            :param folder_name: 本地保存的文件夹名称
            :param workspace_path: (可选) 克隆到的目标根目录，如果不提供则使用默认路径
            """
            # 逻辑：如果 client 传了路径就用 client 的，否则用初始化的默认路径
            root = os.path.abspath(workspace_path) if workspace_path else self.default_workspace

            if not os.path.exists(root):
                os.makedirs(root)

            target_path = os.path.join(root, folder_name)
            if os.path.exists(target_path):
                return f"错误：目录 {target_path} 已存在。"

            try:
                result = subprocess.run(
                    ["git", "clone", repo_url, folder_name],
                    cwd=root,
                    capture_output=True,
                    text=True
                )
                return f"成功克隆至 {target_path}" if result.returncode == 0 else f"失败: {result.stderr}"
            except Exception as e:
                return f"异常: {str(e)}"

        @mcp.tool(name="git_manage")
        async def git_manage(repo_path: str, action: str, message: str = "", branch: str = "main") -> str:
            """
            对本地 Git 仓库执行操作。
            :param repo_path: 仓库的绝对路径或文件夹名（如果是文件夹名，将从默认 workspace 寻找）
            :param action: 执行的动作 (status/pull/push/add/commit/log)
            :param message: commit 时的描述信息
            :param branch: 分支名称
            """
            # 核心改造：判断入参是绝对路径还是仅仅是文件夹名
            if os.path.isabs(repo_path):
                full_path = repo_path
            else:
                full_path = os.path.join(self.default_workspace, repo_path)

            if not os.path.exists(full_path):
                return f"错误：未找到路径 {full_path}"

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
                    cwd=full_path,
                    capture_output=True,
                    text=True
                )
                output = result.stdout if result.returncode == 0 else result.stderr
                return f"[{action.upper()}] 结果:\n{output}"
            except Exception as e:
                return f"执行异常: {str(e)}"