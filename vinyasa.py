import functools
import hashlib
import json
import pickle
import time
import warnings
from pathlib import Path
from tempfile import gettempdir

import typer
from rich import print

CACHE = "vinyasa"
GLOBAL_CONTEXT = {}

app = typer.Typer(name="vinyasa", no_args_is_help=True, help="Vinyasa CLI")
cache_dir = Path(gettempdir(), CACHE)
cache_dir.mkdir(exist_ok=True)

history_dir = Path.home() / ".vinyasa"
history_dir.mkdir(exist_ok=True)
history_file = history_dir / "history.json"


def save_history(scripts) -> None:
    history_data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "scripts": scripts,
    }
    if history_file.exists():
        with open(history_file, "r") as file:
            data = json.load(file)
    else:
        data = []
    data.append(history_data)
    with open(history_file, "w") as file:
        json.dump(data, file, indent=4)


def cache(func):
    """Cache the results of a function.

    The bytecode caching mechanism in vinyasa tracks changes
    in the operational structure and logic of functions,
    rather than variable values or simple text alterations.

    This means that if you change the value of a variable,
    or add a print statement, the function will still be
    cached. However, if you change the order of statements,
    or add a new statement, the function will be re-run.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Get the source code of the function
        # func_source = inspect.getsource(func)
        bytecode = func.__code__.co_code
        key_data = f"{func.__name__}{args}{kwargs}{bytecode}"
        key = hashlib.sha256(key_data.encode()).hexdigest()
        cache_file = cache_dir / f"{key}.pkl"

        if cache_file.exists():
            print(f"Reading from cache: {cache_file} for {func.__name__}")
            with open(cache_file, "rb") as file:
                return pickle.load(file)

        result = func(*args, **kwargs)
        with open(cache_file, "wb") as file:
            pickle.dump(result, file)
        return result

    return wrapper


def resolve_script_path(script) -> Path:
    script_path = Path(script)
    if not script_path.is_absolute():
        script_path = Path.cwd() / script_path
    return script_path


def run_script(script: str) -> None:
    script_path = resolve_script_path(script)
    if not script_path.exists():
        print(f"Script not found: {script}")
        return

    with open(script_path) as f:
        script_str = "\n".join(f.readlines())
        code = compile(script_str, script_path.name, "exec")
        exec(code, GLOBAL_CONTEXT)


@app.command(
    help="""Run a sequence of scripts. 
    Example: vinyasa run load_data.py preprocess.py train.py
    """,
    no_args_is_help=True,
)
def run(
    scripts: list[str] = typer.Argument(..., help="List of scripts to run")
):
    warnings.filterwarnings("ignore")
    save_history(scripts)

    start = time.time()
    for script in scripts:
        run_script(script)
    end = time.time()

    T = end - start
    print(
        f"\n(pipeline) Execution time: {T:.2f} seconds ({T / 60:.2f} minutes)"
    )


@app.command(help="Show history of scripts run.")
def history(
    clear: bool = typer.Option(False, "--clear", help="Clear the history."),
    dump: str = typer.Option(None, "--dump", help="Dump history to a file."),
):
    if clear:
        with open(history_file, "w") as file:
            json.dump([], file)
        print("History cleared.")
        return

    if dump:
        dump_path = Path(dump)
        with open(history_file, "r") as file:
            data = json.load(file)
        with open(dump_path, "w") as dump_file:
            json.dump(data, dump_file, indent=4)
        print(f"History dumped to {dump_path}")
        return

    if history_file.exists():
        with open(history_file, "r") as file:
            data = json.load(file)
            for entry in data:
                cli_call = "vinyasa run " + " ".join(entry["scripts"])
                print(f"{entry['timestamp']}: {cli_call}")
    else:
        print("No history available.")


@app.command(help="Clear all cached function results.")
def clear():
    print("Clearing cache...")
    for cache_file in cache_dir.glob("*.pkl"):
        cache_file.unlink()
    print("Cache cleared.")


if __name__ == "__main__":
    app()
