#!/usr/bin/env python3
"""A process/thread-scoped request against automatic idle system sleep while a bounded worker runs.

Windows `SetThreadExecutionState` asks the OS to keep the system up while the calling thread holds
the request; run_task.py's worker (cmd_worker) acquires it once for its managed lifetime and
releases it in a finally, so the request ends on normal exit, timeout and exceptions - and on a
process death the OS drops it with the thread, so no cleanup path can leak it.

Scope is deliberately narrow: only *automatic idle* system sleep is deferred. The request never
holds the display on (no ES_DISPLAY_REQUIRED), never asks for away mode (no
ES_AWAYMODE_REQUIRED) and cannot block an explicit user sleep/lid action or a power emergency -
the T-072 deadline and watchdog keep their authority, including across a user-initiated nap.
No global power plan, registry value or scheduled task is touched; POSIX has no equivalent and
is a no-op.

Honest reporting: acquire()/release() never pretend. Each returns (ok, detail) where ok is True
only when the API accepted the call; the caller records the outcome durably (attempt log and
attempt record), so a failed request is diagnosable rather than silently assumed.
"""
import ctypes
import os

ES_CONTINUOUS = 0x80000000        # stay in (or return to) the normal execution state
ES_SYSTEM_REQUIRED = 0x00000001   # the system may not idle-sleep while held
ES_DISPLAY_REQUIRED = 0x00000002  # never requested: the display may sleep on its own timer
ES_AWAYMODE_REQUIRED = 0x00000040  # never requested: no away-mode conversion of user sleep


def _windows():
    """os.name seam (tests simulate the platform without patching the real os module)."""
    return os.name == "nt"


def _kernel32():
    """kernel32 seam (tests substitute a mock; never resolved at import, so POSIX stays safe)."""
    return ctypes.windll.kernel32


def acquire():
    """(held, detail): ask Windows to keep this thread's system out of automatic idle sleep.
    held is True only when the API accepted the request (it returns the nonzero previous state);
    a 0 return means failure and is reported as held=False with the reason."""
    if not _windows():
        return False, "not Windows: no idle-sleep request exists or is needed"
    prev = _kernel32().SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED)
    if not prev:
        return False, "SetThreadExecutionState failed (returned 0); running without sleep protection"
    return True, f"ES_SYSTEM_REQUIRED held (previous state 0x{prev & 0xFFFFFFFF:08x})"


def release():
    """(released, detail): clear this thread's request (ES_CONTINUOUS alone). Safe to call only
    after a successful acquire; the same 0-means-failure rule applies."""
    if not _windows():
        return False, "not Windows: nothing to release"
    prev = _kernel32().SetThreadExecutionState(ES_CONTINUOUS)
    if not prev:
        return False, "SetThreadExecutionState(ES_CONTINUOUS) failed (returned 0)"
    return True, f"released (previous state 0x{prev & 0xFFFFFFFF:08x})"
