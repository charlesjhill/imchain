[![SPEC 1 — Lazy Loading of Submodules and Functions](https://img.shields.io/badge/SPEC-1-green?labelColor=%23004811&color=%235CA038)](https://scientific-python.org/specs/spec-0001/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

# imchain

`imchain` is a libary for composable stream processing, with an eye to image processing in particular.

The core unit in the library is the `Operator`, which manipulate iterables. Operators can be combined together to form composable pipelines. Built-in operators are designed to be as lazy as possible to minimize memory use and wasted computation.

```python
import imchain.operator as iop

chain = (
    iop.Effect(print)
    | iop.Map(lambda x: x**2)
    | iop.Filter(lambda x: x % 2 == 0)
    | iop.Effect(print)
    | iop.Take(10)
)

for item in chain.pipe(range(100)):
    ...
```

## Installation

`pip install imchain`

### Contributing

`imchain` uses `uv` for dependency management. After cloning the repo, recreate the project virtual environment with development dependencies and install the pre-commit hooks:

```bash
uv sync
uv run pre-commit install
```
