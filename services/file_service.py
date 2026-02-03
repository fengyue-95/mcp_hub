import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP

_DEFAULT_BASE_DIR = os.getenv("FILE_SERVICE_BASE_DIR", os.getcwd())
_MAX_READ_BYTES = int(os.getenv("FILE_SERVICE_MAX_READ_BYTES", "104857600"))  # 1 MiB
_MAX_WRITE_BYTES = int(os.getenv("FILE_SERVICE_MAX_WRITE_BYTES", "104857600"))  # 1 MiB
_DEFAULT_ENCODING = os.getenv("FILE_SERVICE_ENCODING", "utf-8")


class FileService:
    """处理文件相关操作的服务模块"""

    def register_tools(self, mcp: FastMCP):
        @mcp.tool(name="file_read")
        async def read_file(path: str, encoding: Optional[str] = None) -> str:
            """读取本地文件内容（受限于基础目录与大小限制）"""
            file_path = _resolve_path(path)
            _ensure_readable_file(file_path)
            size = file_path.stat().st_size
            if size > _MAX_READ_BYTES:
                raise ValueError(f"File too large to read: {size} bytes (limit {_MAX_READ_BYTES}).")
            text = file_path.read_text(encoding=encoding or _DEFAULT_ENCODING)
            return text

        @mcp.tool(name="file_write")
        async def write_file(
            path: str,
            content: str,
            encoding: Optional[str] = None,
            create_dirs: bool = True,
        ) -> str:
            """写入内容到本地文件（原子写入、受限于基础目录与大小限制）"""
            if not isinstance(content, str):
                raise TypeError("content must be a string.")
            data = content.encode(encoding or _DEFAULT_ENCODING)
            if len(data) > _MAX_WRITE_BYTES:
                raise ValueError(
                    f"Content too large to write: {len(data)} bytes (limit {_MAX_WRITE_BYTES})."
                )
            file_path = _resolve_path(path)
            if create_dirs:
                file_path.parent.mkdir(parents=True, exist_ok=True)
            _ensure_writable_path(file_path)
            _atomic_write(file_path, data, encoding or _DEFAULT_ENCODING)
            return f"Wrote {len(data)} bytes to {file_path}."


def _resolve_path(path: str) -> Path:
    if not path or not isinstance(path, str):
        raise ValueError("path must be a non-empty string.")
    base_dir = Path(_DEFAULT_BASE_DIR).expanduser().resolve()
    target = Path(path).expanduser()
    if not target.is_absolute():
        target = base_dir / target
    try:
        target = target.resolve()
    except FileNotFoundError:
        target = target.parent.resolve() / target.name
    if base_dir != target and base_dir not in target.parents:
        raise PermissionError("path is outside of base directory.")
    return target


def _ensure_readable_file(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if not path.is_file():
        raise IsADirectoryError(f"Not a file: {path}")
    if not os.access(path, os.R_OK):
        raise PermissionError(f"File not readable: {path}")


def _ensure_writable_path(path: Path) -> None:
    if path.exists() and not path.is_file():
        raise IsADirectoryError(f"Not a file: {path}")
    parent = path.parent
    if not parent.exists():
        return
    if not os.access(parent, os.W_OK):
        raise PermissionError(f"Directory not writable: {parent}")


def _atomic_write(path: Path, data: bytes, encoding: str) -> None:
    tmp_dir = path.parent
    with tempfile.NamedTemporaryFile(delete=False, dir=tmp_dir) as tmp:
        tmp.write(data)
        tmp.flush()
        os.fsync(tmp.fileno())
        temp_name = tmp.name
    try:
        shutil.move(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)
