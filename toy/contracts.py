"""
Exploration of implementing function contracts: pre and post conditions.
All preconditions must be satisfied before the function call.
All postconditions must be satisfied after the function call.

What if instead of evaluating post-conditions, we can do property testing to guarantee the results?

Ref:
- https://github.com/life4/deal
"""
import inspect
from typing import Any, Callable, TypeVar

T = TypeVar("T")


class PreCondError(Exception):
    pass


class PostCondError(Exception):
    pass


CondList = list[str] | None


def safe_eval(expr: str, kwargs: dict[str, Any]) -> bool:
    code = compile(expr, "<string>", mode="eval")
    return eval(code, {}, kwargs)


def contract(pre: CondList = None, post: CondList = None) -> Callable:
    def wrapper(func):
        def _inner(*args, **kwargs):
            for param in inspect.signature(func).parameters.values():
                if param.kind != param.KEYWORD_ONLY:
                    raise PreCondError(f"Parameter <{param}> is not keyword only!")

            for cond in pre or []:
                try:
                    assert safe_eval(cond, kwargs)
                except Exception as e:
                    raise PreCondError(
                        f"Precondition <{cond}> was not satisfied!"
                    ) from e

            ret = func(*args, **kwargs)

            for cond in post or []:
                try:
                    assert safe_eval(cond, kwargs | {"_ret": ret})
                except Exception as e:
                    raise PostCondError(
                        f"Postcondition <{cond}> was not satisfied!"
                    ) from e

        return _inner

    return wrapper


@contract(
    pre=[
        "xs == sorted(xs)",
        "len(xs) == len(set(xs))",
    ],
    post=[
        "_ret is None or 0 <= _ret < len(xs)",
    ],
)
def binary_search(*, x: T, xs: list[T]) -> int | None:
    lo, hi = 0, len(xs) - 1

    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if xs[mid] == x:
            return mid
        if xs[mid] < x:
            lo = mid + 1
        else:
            hi = mid - 1

    return None


@contract(post=["xs == sorted(xs)"])
def bubble_sort(*, xs: list[T]) -> list[T]:
    lim = len(xs)

    while lim > 0:
        swapped = False

        for i in range(1, lim):
            if xs[i] < xs[i - 1]:
                xs[i], xs[i - 1] = xs[i - 1], xs[i]
                swapped = True

        if not swapped:
            break

        lim -= 1

    return xs


if __name__ == "__main__":
    i = binary_search(x=10, xs=[-2, 0, 1, 5, 19])

    import numpy as np

    for _ in range(100):
        xs: list[int] = np.random.randint(-100, 100, size=1000).tolist()
        bubble_sort(xs=xs)
