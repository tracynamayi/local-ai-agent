import ast
import operator
import platform
import shutil
import sys
from datetime import datetime
from pathlib import Path

from langchain_core.tools import tool

#all file operation will be restricted to this folder for safety
WORKSPACE = Path(__file__).parent / "workspace"
WORKSPACE.mkdir(exist_ok=True)

def _safe_path(filename: str) -> Path:
    """Resolve a filename inside WORKSPACE and block path escapes like ..\\..\\"""
    path =(WORKSPACE / filename).resolve()
    if not path.is_relative_to(WORKSPACE.resolve()):
        raise ValueError("Access outside the workspace folder is not allowed.")
    return path

@tool
def read_file(filename: str) -> str:
    """Read the text content of a file from the workspace folder.
    Use this when the user asks to open, read, or view a file."""
    try:
        path = _safe_path(filename)
        if not path.exists():
            return f"Error: '{filename}' does not exist in the workspace."
        return path.read_text(encoding="utf-8")
    except Exception as e:
        return f"Error reading file: {e}"


@tool
def write_file(filename: str, content: str) -> str:
    """Write text to a file in the workspace folder, creating it or
    overwriting it. Use this when the user asks to save or create a file."""
    try:
        path = _safe_path(filename)
        path.write_text(content, encoding="utf-8")
        return f"Successfully wrote {len(content)} characters to '{filename}'."
    except Exception as e:
        return f"Error writing file: {e}"


@tool
def get_system_info() -> str:
    """Get information about this computer: operating system, Python
    version, and free disk space. Use this when asked about the system."""
    disk = shutil.disk_usage(Path.cwd().anchor)
    free_gb = disk.free / (1024 ** 3)
    total_gb = disk.total / (1024 ** 3)
    return (
        f"OS: {platform.system()} {platform.release()}\n"
        f"Machine: {platform.machine()}\n"
        f"Python: {sys.version.split()[0]}\n"
        f"Disk: {free_gb:.1f} GB free of {total_gb:.1f} GB"
    )


# ---------- Calculator and date tools ----------

_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
}


def _eval_node(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPERATORS:
        left, right = _eval_node(node.left), _eval_node(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > 100:
            raise ValueError("Exponent too large.")
        return _OPERATORS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPERATORS:
        return _OPERATORS[type(node.op)](_eval_node(node.operand))
    raise ValueError("Unsupported expression.")


@tool
def calculator(expression: str) -> str:
    """Evaluate a math expression such as '(12 + 8) * 3 / 4'.
    Supports + - * / ** and %. Always use this for arithmetic
    instead of calculating in your head."""
    try:
        tree = ast.parse(expression, mode="eval")
        return str(_eval_node(tree.body))
    except Exception as e:
        return f"Error: could not evaluate '{expression}' ({e})"


@tool
def get_current_datetime() -> str:
    """Get the current local date, time, and day of the week."""
    return datetime.now().strftime("%A, %Y-%m-%d %H:%M:%S")


# The agent will import this list in Step 4.
TOOLS = [read_file, write_file, get_system_info, calculator, get_current_datetime]


if __name__ == "__main__":
    # Quick manual check: run `python tools.py`
    print(get_current_datetime.invoke({}))
    print(calculator.invoke({"expression": "(12 + 8) * 3 / 4"}))
    print(write_file.invoke({"filename": "hello.txt", "content": "Hi from tools.py"}))
    print(read_file.invoke({"filename": "hello.txt"}))
    print(get_system_info.invoke({}))