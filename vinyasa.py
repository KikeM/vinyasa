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


def save_full_script(scripts: list[str], full_script: str) -> None:
    """Save a full script to a file.

    Parameters
    ----------
    scripts : list[str]
        List of scripts to run.
    full_script : str
        Path to save the full script to.

    Notes
    -----
    The full script is a concatenation of all the scripts
    in the pipeline, separated by two newlines.
    """
    # Add .py extension if not present
    if not full_script.endswith(".py"):
        full_script += ".py"

    print(f"Dumping full script to {full_script} ...")
    full_script_path = Path(full_script)
    with open(full_script_path, "w") as full_file:
        for script in scripts:
            script_path = resolve_script_path(script)
            with open(script_path) as f:
                full_file.write(f.read() + "\n\n")

    print(f"Full script dumped to {full_script_path}")


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
    """Cache the results of a function, based on its arguments and bytecode.

    The arguments need to have a valid `__repr__` method.

    Notes
    -----
    The bytecode caching mechanism tracks changes
    in the operational structure and logic of functions,
    rather than variable values or simple text alterations.

    This means that if you change the value of a variable,
    or add a print statement, the function will still be
    cached. However, if you change the order of statements,
    or add a new statement, the function will be re-run.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        bytecode = func.__code__.co_code
        key_data = f"{func.__name__}{args}{kwargs}{bytecode}"
        key = hashlib.sha256(key_data.encode()).hexdigest()
        cache_file = cache_dir / f"{key}.pkl"

        if cache_file.exists():
            print(f"({func.__name__}) Reading from cache: {cache_file}")
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
    scripts: list[str] = typer.Argument(..., help="List of scripts to run"),
    full_script: str = typer.Option(
        None,
        "--full-script",
        help="Dump full script to a file.",
    ),
):
    warnings.filterwarnings("ignore")
    save_history(scripts)

    if full_script:
        save_full_script(scripts=scripts, full_script=full_script)

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
    unique: bool = typer.Option(
        False, "--unique", help="Show only unique script runs."
    ),
):
    if clear:
        with open(history_file, "w") as file:
            json.dump([], file)
        print("History cleared.")
        return

    if history_file.exists():
        with open(history_file, "r") as file:
            history_data = json.load(file)

    else:
        print("No history available.")
        return

    if unique:
        unique_runs = set(
            [
                "vinyasa run " + " ".join(entry["scripts"])
                for entry in history_data
            ]
        )

        for entry in unique_runs:
            print(entry)

        history_data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "scripts": list(unique_runs),
        }

    else:
        for entry in history_data:
            cli_call = "vinyasa run " + " ".join(entry["scripts"])
            print(f"{entry['timestamp']}: {cli_call}")

    if dump:
        dump_path = Path(dump)
        with open(dump_path, "w") as dump_file:
            json.dump(history_data, dump_file, indent=4)
        print(f"History dumped to {dump_path}")


@app.command(help="Clear all cached function results.")
def clear():
    print("Clearing cache...")
    for cache_file in cache_dir.glob("*.pkl"):
        cache_file.unlink()
    print("Cache cleared.")


if __name__ == "__main__":
    app()
