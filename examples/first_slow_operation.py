from time import sleep

from vinyasa import cache

print("I am a script that takes a long time to run! Please cache me!")


@cache
def load_data(path: str) -> int:
    print("Loading data...")
    sleep(5)

    value_to_return = 5  # <---- change this won't change bytecode, hence it won't update the cache

    print("Data loaded!")
    return value_to_return


path = "data.csv"  # changing this will update the cache
a = load_data(path=path)
print(a)
