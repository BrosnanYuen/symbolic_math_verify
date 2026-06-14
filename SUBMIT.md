# PyPI Submission

## Package Name

The project is packaged as `symbolic-math-verify` and imported as `symbolic_math_verify`.

## Before You Submit

1. Confirm the version in [pyproject.toml](/home/brosnan/symbolic_math_verify/symbolic_math_verify/pyproject.toml) is new.
2. Make sure the working tree is clean.
3. Run the test suite:

```bash
.venv/bin/python tests/run_parallel_unittest.py
```

## Build The Distribution

Install the build tools if needed:

```bash
.venv/bin/python -m pip install --upgrade build twine
```

Build the source distribution and wheel:

```bash
.venv/bin/python -m build
```

This creates:

- `dist/symbolic_math_verify-<version>.tar.gz`
- `dist/symbolic_math_verify-<version>-py3-none-any.whl`

## Validate The Artifacts

Check the packages before upload:

```bash
.venv/bin/python -m twine check dist/*
```

## Upload To TestPyPI

Upload the build artifacts to TestPyPI first:

```bash
.venv/bin/python -m twine upload --repository testpypi dist/*
```

Smoke test install from TestPyPI:

```bash
.venv/bin/python -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple symbolic-math-verify
```

## Upload To PyPI

When TestPyPI looks correct, upload the same artifacts to PyPI:

```bash
.venv/bin/python -m twine upload dist/*
```

## Recommended Release Flow

1. Update the version in [pyproject.toml](/home/brosnan/symbolic_math_verify/symbolic_math_verify/pyproject.toml).
2. Run tests.
3. Build with `.venv/bin/python -m build`.
4. Validate with `.venv/bin/python -m twine check dist/*`.
5. Upload to TestPyPI.
6. Install and import the package from TestPyPI.
7. Upload to PyPI.

## Smoke Test

```python
from symbolic_math_verify import extract_variables
from symbolic_math_verify import is_calculation_correct
from symbolic_math_verify import is_equation_equal
from symbolic_math_verify import is_subscript_substitution_correct
from symbolic_math_verify import is_substitution_correct
from symbolic_math_verify import verify_yaml_file
```
