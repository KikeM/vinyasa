print("I am a script that reuses the results from previous steps!")


def square(x: int) -> int:
    return x**2


print(f"{a=}")  # the linter will complain about this,
# because it's not defined in this file
# I add type : ignore to the line above to remove the warning
a = square(a)  # type : ignore
print(f"{a=}")
