from __future__ import annotations

import base64
import io
import os
import runpy
import shlex
import sys
import traceback
from pathlib import Path

PROJECT_DIR = Path("/home/pyodide/project")

_command = ""
_entry_point = ""
_show_image = None

def setup(command: str, entry_point: str, show_image) -> None:
    global _command, _entry_point, _show_image
    _command, _entry_point, _show_image = command, entry_point, show_image
    
    os.chdir(PROJECT_DIR)
    sys.path.insert(0, str(PROJECT_DIR))
    _patch_matplotlib()
    print(f"Python {sys.version.split()[0]} ready. Type 'help' for commands.")
    
def run_command(line: str) -> None:
    try:
        parts = shlex.split(line)
    except ValueError as exc:
        print(f"Couldn't parse that: {exc}", file=sys.stderr)
        return
    if not parts:
        return

    name, args = parts[0], parts[1:]
    if name == "python" and args[:1] == [_entry_point]:
        name, args = _command, args[1:]
        
    try:
        if name == _command:
            _run_entry_point(args)
        elif name == "help":
            _print_help()
        elif name == "ls":
            target = Path(args[0]) if args else Path(".")
            for path in sorted(target.iterdir()):
                print(path.name + ("/" if path.is_dir() else ""))
        elif name == "cat" and args:
            print(Path(args[0]).read_text())
        else:
            print(f"{name}: command not found. Type 'help'.", file=sys.stderr)
    except OSError as exc:
        print(exc, file=sys.stderr)
        
def _run_entry_point(args: list[str]) -> None:
    sys.argv = [_entry_point, *args]
    try:
        if _entry_point.endswith(".py"):
            runpy.run_path(_entry_point, run_name="__main__")
        else:
            runpy.run_module(_entry_point, run_name="__main__", alter_sys=True)
    except SystemExit as exc:
        if isinstance(exc.code, str):
            print(exc.code, file=sys.stderr)
        elif exc.code not in (None, 0):
            print(f"(exited with status {exc.code})", file=sys.stderr)
    except Exception:
        traceback.print_exc()
    finally:
        sys.stdout.flush()
        sys.stderr.flush()
        
def _print_help() -> None:
    rows = [
        (f"{_command} [options]", f"run the project ({_entry_point}). Try: {_command} --help"),
        ("ls [folder]", "list the project's files"),
        ("cat <file>", "show a file's source"),
        ("clear", "clear the screen"),
        ("help", "show this message"),
        ("↑ / ↓", "scroll through previous commands"),
    ]
    width = max(len(left) for left, _ in rows) + 3
    for left, right in rows:
        print(f"  {left.ljust(width)}{right}")

def _patch_matplotlib() -> None:
    try:
        import matplotlib
    except ImportError:
        return
    
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    
    def show(*args, **kwargs) -> None:
        for number in plt.get_fignums():
            buffer = io.BytesIO()
            plt.figure(number).savefig(buffer, format="png", dpi=100, bbox_inches="tight")
            _show_image(base64.b64encode(buffer.getvalue()).decode())
        plt.close("all")
    
    plt.show = show