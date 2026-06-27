"""语音运行时小工具：密钥路径 + 原子写 + 后台派生（跨平台）。仅语音用。"""
import os
import tempfile

HOME = os.path.expanduser("~")
IS_WINDOWS = os.name == "nt"
RUNTIME_DIR = os.environ.get("SBO_RUNTIME_DIR") or os.path.join(HOME, ".second-brain-obsidian")
SECRETS_PATH = os.path.join(RUNTIME_DIR, "secrets.env")


def ensure_runtime_dir():
    os.makedirs(RUNTIME_DIR, exist_ok=True)


def atomic_write(path, text):
    """原子写：临时文件 + os.replace。"""
    d = os.path.dirname(path) or "."
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_sbo_")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def detach_kwargs():
    """后台派生子进程脱离父进程（跨平台）：POSIX setsid / Windows DETACHED_PROCESS。"""
    if IS_WINDOWS:
        return {"creationflags": 0x00000008 | 0x00000200}
    return {"start_new_session": True}
