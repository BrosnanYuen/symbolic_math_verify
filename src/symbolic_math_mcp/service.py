"""Core verification service used by the FastMCP tool."""

from __future__ import annotations

import threading
import time
from concurrent.futures import Future, ThreadPoolExecutor, TimeoutError
from collections.abc import Iterable
from pathlib import Path
from typing import Callable

from symbolic_math_verify import verify_yaml_file


Verifier = Callable[[str], str]


class SymbolicMathService:
    """Synchronously validate YAML files while enforcing queue and timeout limits."""

    def __init__(
        self,
        max_requests: int,
        total_timeout: float,
        yaml_must_have: tuple[str, ...] = (),
        verifier: Verifier = verify_yaml_file,
    ) -> None:
        if max_requests <= 0:
            raise ValueError("max_requests must be greater than zero")
        if total_timeout <= 0:
            raise ValueError("total_timeout must be greater than zero")
        self._total_timeout = float(total_timeout)
        self._yaml_must_have = tuple(yaml_must_have)
        self._verifier = verifier
        self._slots = threading.Semaphore(max_requests)
        self._executor = ThreadPoolExecutor(max_workers=max_requests, thread_name_prefix="symbolic-math-verify")

    def shutdown(self) -> None:
        """Release executor resources."""
        self._executor.shutdown(wait=False, cancel_futures=True)

    def check_symbolic_math(self, filename: str) -> dict[str, str]:
        """Validate one YAML file and return the required synchronous response payload."""
        started = time.monotonic()
        normalized_name = str(filename)
        acquired = self._slots.acquire(timeout=self._total_timeout)
        if not acquired:
            return _timeout_response(normalized_name)
        try:
            path = Path(normalized_name)
            checked = _check_yaml_file(path, self._yaml_must_have)
            if checked is not None:
                return checked

            remaining = self._total_timeout - (time.monotonic() - started)
            if remaining <= 0:
                return _timeout_response(normalized_name)

            future = self._executor.submit(self._verifier, normalized_name)
            try:
                result = future.result(timeout=remaining)
            except TimeoutError:
                future.cancel()
                return _timeout_response(normalized_name)
            except Exception:
                return _unknown_error_response(normalized_name)
            return _success_response(normalized_name, result)
        finally:
            self._slots.release()

    def check_symbolic_math_parallel(self, dir_path: str) -> dict[str, object]:
        """Validate every YAML file in a directory and return one synchronous aggregate response."""
        started = time.monotonic()
        normalized_dir = str(dir_path)
        acquired = self._slots.acquire(timeout=self._total_timeout)
        if not acquired:
            return _timeout_response(normalized_dir)
        try:
            directory = Path(normalized_dir)
            if not directory.is_absolute() or not directory.exists() or not directory.is_dir():
                return _file_not_found_response(normalized_dir)
            try:
                yaml_paths = sorted(
                    path for path in directory.iterdir() if path.is_file() and path.suffix.lower() == ".yaml"
                )
            except FileNotFoundError:
                return _file_not_found_response(normalized_dir)
            except OSError:
                return _file_read_error_response(normalized_dir)
            if not yaml_paths:
                return _file_not_found_response(normalized_dir)

            normalized_paths: list[str] = []
            for path in yaml_paths:
                checked = _check_yaml_file(path, self._yaml_must_have)
                if checked is not None:
                    return checked
                normalized_paths.append(str(path))

            remaining = self._total_timeout - (time.monotonic() - started)
            if remaining <= 0:
                return _timeout_response(normalized_dir)

            futures: dict[str, Future[str]] = {
                filename: self._executor.submit(self._verifier, filename)
                for filename in normalized_paths
            }

            results: dict[str, str] = {}
            for filename, future in futures.items():
                remaining = self._total_timeout - (time.monotonic() - started)
                if remaining <= 0:
                    future.cancel()
                    _cancel_futures(futures.values())
                    return _timeout_response(normalized_dir)
                try:
                    results[filename] = future.result(timeout=remaining)
                except TimeoutError:
                    future.cancel()
                    _cancel_futures(futures.values())
                    return _timeout_response(normalized_dir)
                except Exception:
                    _cancel_futures(futures.values())
                    return _unknown_error_response(normalized_dir)
            return _parallel_success_response(normalized_dir, results)
        finally:
            self._slots.release()


def _cancel_futures(futures: Iterable[Future[str]]) -> None:
    for future in futures:
        future.cancel()


def _check_yaml_file(path: Path, yaml_must_have: tuple[str, ...] = ()) -> dict[str, str] | None:
    normalized_name = str(path)
    if path.suffix.lower() != ".yaml":
        return _file_not_found_response(normalized_name)
    if not path.exists() or not path.is_file():
        return _file_not_found_response(normalized_name)
    try:
        content = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return _file_not_found_response(normalized_name)
    except OSError:
        return _file_read_error_response(normalized_name)
    missing_strings = [item for item in yaml_must_have if item not in content]
    if missing_strings:
        return _missing_yaml_string_response(normalized_name, missing_strings)
    return None


def _success_response(filename: str, result: str) -> dict[str, str]:
    return {
        "status": "Tool call completed!",
        "filename": filename,
        "result": result,
    }


def _parallel_success_response(dir_path: str, result: dict[str, str]) -> dict[str, object]:
    return {
        "status": "Parallel Tool call completed!",
        "dir_path": dir_path,
        "result": result,
    }


def _timeout_response(filename: str) -> dict[str, str]:
    return {
        "status": "Tool call has timed out!",
        "filename": filename,
        "result": "TIMEOUT ERROR!",
    }


def _file_not_found_response(filename: str) -> dict[str, str]:
    return {
        "status": "Tool call cannot find the file based on the filename!",
        "filename": filename,
        "result": "FILE NOT FOUND!",
    }


def _file_read_error_response(filename: str) -> dict[str, str]:
    return {
        "status": "Tool call cannot read the file!",
        "filename": filename,
        "result": "FILE CANNOT BE READ!",
    }


def _missing_yaml_string_response(filename: str, missing_strings: list[str]) -> dict[str, str]:
    return {
        "status": "Missing a string from the .yaml file!",
        "filename": filename,
        "result": ", ".join(missing_strings),
    }


def _unknown_error_response(filename: str) -> dict[str, str]:
    return {
        "status": "Tool call has unknown error!",
        "filename": filename,
        "result": "UNKNOWN ERROR!",
    }
