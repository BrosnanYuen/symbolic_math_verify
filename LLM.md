# symbolic_math_mcp Guide

Use `symbolic_math_mcp.check_symbolic_math(filename)` to validate one symbolic math YAML proof file.
Use `symbolic_math_mcp.check_symbolic_math_parallel(dir_path)` to validate every symbolic math YAML proof file in one absolute directory.

## Tool Contract

- `check_symbolic_math(filename)`
  Input must be an absolute filepath ending in `.yaml`.
  Output is a JSON object with `status`, `filename`, and `result`.

Single-file proof is valid:
```json
{
  "status": "Tool call completed!",
  "filename": "/abs/path/proof.yaml",
  "result": "Math proofs are valid"
}
```

Single-file proof is invalid:
```json
{
  "status": "Tool call completed!",
  "filename": "/abs/path/proof.yaml",
  "result": "Error! Math proofs are invalid"
}
```

- `check_symbolic_math_parallel(dir_path)`
  Input must be an absolute directory path.
  The tool scans that directory for `.yaml` files, starts one verification task per file, respects the server's `max_requests` limit, and blocks until all results are ready or the total timeout is exceeded.
  Output is a JSON object with `status`, `dir_path`, and `result`.

Parallel proof check:
```json
{
  "status": "Parallel Tool call completed!",
  "dir_path": "/abs/path/proofs",
  "result": {
    "/abs/path/proofs/one.yaml": "Math proofs are valid",
    "/abs/path/proofs/two.yaml": "Error! Math proofs are invalid"
  }
}
```

Guidance:
- Always pass absolute paths.
- Use `check_symbolic_math` for one file.
- Use `check_symbolic_math_parallel` for a directory of `.yaml` files.
- Treat any result other than `"Math proofs are valid"` as a failed verification.
- Strongly prefer `check_symbolic_math_parallel` over `check_symbolic_math` for multiple files
