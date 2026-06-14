# PyPI Submission

## Before You Submit

1. Set the real project URLs in `pyproject.toml`.
2. Confirm the version in `pyproject.toml` is new and not already on PyPI.
3. Run the test suite:

```bash
.venv/bin/python -m unittest discover -s tests
```

## Build The Distribution

Install the build tools if needed:

```bash
python -m pip install --upgrade build twine
```

Create source and wheel distributions from the project root:

```bash
python -m build
```

This should create:

- `dist/symbolic_math_verify-<version>.tar.gz`
- `dist/symbolic_math_verify-<version>-py3-none-any.whl`

## Validate The Artifacts

Check the built packages before upload:

```bash
python -m twine check dist/*
```

## Upload To TestPyPI First

Upload to TestPyPI:

```bash
python -m twine upload --repository testpypi dist/*
```

Install from TestPyPI to verify the package:

```bash
python -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple symbolic-math-verify
```

## Upload To PyPI

When TestPyPI looks correct, upload the same artifacts to PyPI:

```bash
python -m twine upload dist/*
```

## Recommended Release Flow

1. Update `pyproject.toml` version.
2. Run tests.
3. Build with `python -m build`.
4. Validate with `python -m twine check dist/*`.
5. Upload to TestPyPI.
6. Smoke test install/import.
7. Upload to PyPI.

## Smoke Test

After install, verify the public API:

```python
from symbolic_math_verify import is_equation_equal
from symbolic_math_verify import is_substitution_correct
from symbolic_math_verify import is_subscript_substitution_correct
from symbolic_math_verify import is_calculation_correct
from symbolic_math_verify import extract_variables
from symbolic_math_verify import verify_yaml_file
```
