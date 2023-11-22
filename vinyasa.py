import functools
import hashlib
import inspect
import pickle
import time
import warnings
from pathlib import Path
from tempfile import gettempdir

import typer
from rich import print

CACHE = "vinyasa"
GLOBAL_CONTEXT = {}

app = typer.Typer()
cache_dir = Path(gettempdir(), CACHE)
cache_dir.mkdir(exist_ok=True)


def cache(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Get the source code of the function
        # func_source = inspect.getsource(func)
        # key_data = f"{func.__name__}{args}{kwargs}{func_source}"

        key_data = f"{func.__name__}{args}{kwargs}"
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


def resolve_script_path(script):
    script_path = Path(script)
    if not script_path.is_absolute():
        script_path = Path.cwd() / script_path
    return script_path


def run_script(script: str):
    script_path = resolve_script_path(script)
    if not script_path.exists():
        print(f"Script not found: {script}")
        return

    with open(script_path) as f:
        script_str = "\n".join(f.readlines())
        code = compile(script_str, script_path.name, "exec")
        exec(code, GLOBAL_CONTEXT)


@app.command()
def run(
    scripts: list[str] = typer.Argument(..., help="List of scripts to run")
):
    warnings.filterwarnings("ignore")

    start = time.time()
    for script in scripts:
        run_script(script)
    end = time.time()

    T = end - start
    print(
        f"\n(pipeline) Execution time: {T:.2f} seconds ({T / 60:.2f} minutes)"
    )


if __name__ == "__main__":
    app()
