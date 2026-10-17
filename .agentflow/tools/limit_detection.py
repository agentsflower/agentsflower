"""Shared provider/account limit detection for AgentFlow session logs.

  python limit_detection.py <logfile> [--exit-code N]

Prints ``limit: <matched phrase>`` and exits 0 when the tool's own output near
the end of the log shows a provider/account limit, ``no limit`` and exit 1
otherwise (exit 2 on usage errors). Used by run_task.py (worker ``limitHit``),
conductor.ps1 (background Orchestrator ``limitHit``) and tick.py
(``hit_limit``/``learn_limits``), so a session log is judged the same way
everywhere.

A limit is the tool's own provider reporting account budget exhaustion or
disabled access. The same words inside a worker's report, product code or test
output ("per-video quota reservation", "rate limits are per process",
"QUOTA_EXCEEDED") are subject matter, not a provider error. Two signal classes:

- strong: provider-directed phrasing - "hit your usage limit", "out of
  credits", "subscription access ... disabled", "ask your admin to enable
  access". It counts even on a clean exit: a tool can end 0 and still be
  limited.
- weak: bare status codes and qualified quota/limit words -
  RESOURCE_EXHAUSTED, QUOTA_EXCEEDED, "quota reached", "usage limit reached",
  "rate limit exceeded", "usage window exhausted", "insufficient_quota". They
  count only with evidence that the tool itself failed: a nonzero exit code,
  an error-prefixed log line, or an outer error event in a structured
  (stream-json) log - as opposed to quoted assistant/tool/test content.

Quoted data is not the provider's own error: the content of structured
non-error events (assistant, tool, successful result) is skipped entirely,
and on a plain line a phrase framed as quoted output ("test failed:
expected 200, got 429 <phrase>", "the API responded: '<phrase>'", a report
verb like "the banner shows \"<phrase>\"" or an already-open quote span)
stays subject matter. A bare provider sentence or an error-prefixed line
keeps counting at any exit code.

Retryable transport failures (UNAVAILABLE, connection refused, timeouts, 5xx)
match no pattern: they stay normal retry/fallback errors, never a budget hold.
"""
import argparse
import json
import re
import sys
from pathlib import Path

TAIL_CHARS = 8000  # the final state matters: an early transient error later retried is not a limit

# Provider-directed phrasing: counts regardless of exit code. Two kinds decide how a
# recorded hold scopes (tick.py): "account" failures disable the whole tool identity
# (subscription, access, credits); "quota" failures may hold only the session's quota
# group when the attempt's model names one.
_ACCOUNT = [
    r"out of credits",
    r"disabled[^\r\n]{0,80}subscription access|subscription access[^\r\n]{0,80}disabled",
    r"ask your admin to enable access",
    r"(?:account|api|subscription) access (?:has been |is |was )?(?:disabled|revoked|suspended)",
]
_QUOTA_STRONG = [
    r"hit your (?:[\w-]+ )?limits?",
    r"you(?:'ve| have) (?:hit|reached|exceeded|used up) your (?:[\w-]+ )?(?:limit|quota|credit)",
    r"your (?:[\w-]+ ){0,3}(?:limits?|quotas?|credits?|allowance) (?:has been |is |was )?(?:reached|exceeded|exhausted|depleted)",
    r"your (?:[\w-]+ ){0,3}limits? resets?\b",
]
_STRONG = _ACCOUNT + _QUOTA_STRONG

# Ambiguous status codes and qualified limit words: count only in an outer
# error context (structured event or "error:" line) or when the run failed.
_WEAK = [
    r"resource_exhausted",
    r"quota[ _-]?exceeded",
    r"\bquotas? (?:has been |is |was )?(?:reached|exhausted|depleted)",
    r"(?:usage|session|account|monthly|daily|weekly|credit|token|spend|request|api|rate)[ _-]?limits? "
    r"(?:has been |is |was )?(?:reached|exceeded|exhausted|hit)",
    r"rate_limit_error|insufficient_quota|too many requests",
    r"(?:usage|token|credit|request)[ _-]?windows? (?:has been |is |was )?(?:exhausted|exceeded|reached)",
    r"(?:limit|quota|credit|usage|window)[^\r\n]{0,30}\bresets? (?:in|at) \d",
]

_STRONG_RE = [re.compile(p, re.I) for p in _STRONG]
_ACCOUNT_RE = [re.compile(p, re.I) for p in _ACCOUNT]
_QUOTA_STRONG_RE = [re.compile(p, re.I) for p in _QUOTA_STRONG]
_WEAK_RE = [re.compile(p, re.I) for p in _WEAK]

# A plain line that is itself an error report, not report prose about errors.
_OUTER_LINE = re.compile(r"^\s*(?:[\w.]+ )?(?:error|fatal|panic|exception)\b", re.I)

# Framing before a match that marks it as quoted subject matter, not the
# tool's own report: test/assertion output, an HTTP status in a check, or
# reported speech ("the API responded: 'out of credits'", "the banner shows
# 'out of credits'").
_QUOTE_FRAME = re.compile(
    r"\b(?:expected|assert(?:ion|ed)?|tests?|fixtures?|got|returned|"
    r"responded|replied|reported|print(?:ed|s)?|output|response|said|says|"
    r"quote[ds]?|show[ns]?|displays?(?:ed)?|wrote|writ(?:es?|ten)|"
    r"echo(?:es|ed)?|stderr|stdout)\b|status\s+(?:code\s+)?\d",
    re.I,
)

# Fields of a structured error event that carry the provider's message.
_ERROR_FIELDS = ("error", "errors", "message", "reason", "detail", "status", "result", "data")


def _strings(obj):
    if isinstance(obj, str):
        return [obj]
    if isinstance(obj, dict):
        return [s for v in obj.values() for s in _strings(v)]
    if isinstance(obj, list):
        return [s for v in obj for s in _strings(v)]
    return []


def _json_events(obj):
    """(text, outer, quoted) candidates from one parsed stream-json event.

    The outer agent's own error/result-failure event is an outer candidate;
    assistant, tool and successful result content is quoted data: the explicit
    non-error classification wins over any strong phrase inside it.
    """
    if not isinstance(obj, dict):
        yield " ".join(_strings(obj)), False, True
        return
    t = str(obj.get("type", "")).lower()
    is_err = (t == "error" or bool(obj.get("error")) or bool(obj.get("is_error"))
              or "error" in str(obj.get("subtype", "")).lower())
    if is_err:
        parts = [s for k in _ERROR_FIELDS for s in _strings(obj.get(k))]
        yield " ".join(parts) or " ".join(_strings(obj)), True, False
    else:
        yield " ".join(_strings(obj)), False, True


def _candidates(text):
    for raw in (text or "").splitlines():
        line = raw.strip()
        if not line:
            continue
        if line[0] == "{":
            try:
                yield from _json_events(json.loads(line))
            except ValueError:
                yield line, bool(_OUTER_LINE.match(line)), False
            continue
        yield line, bool(_OUTER_LINE.match(line)), False


def _inside_quote(prefix):
    """True when `prefix` ends inside an unclosed quoted span: report prose that
    quotes the provider verbatim ("the transcript contains '<phrase>'"). An
    apostrophe inside a word ("you've") is no delimiter, and a closing or
    possessive `'` opens no span."""
    inside = None
    n = len(prefix)
    for i, c in enumerate(prefix):
        if c not in "\"'`":
            continue
        if inside is None:
            if c == "'" and i and prefix[i - 1].isalnum():
                continue  # a closing or possessive apostrophe opens no span
            inside = c
        elif c == inside and not (c == "'" and i + 1 < n
                                  and prefix[i - 1].isalnum() and prefix[i + 1].isalnum()):
            inside = None
    return inside is not None


def _quoted(candidate, start):
    """True when the match at `start` sits inside report prose that quotes the
    phrase: test/assertion output, an HTTP status result, reported speech or an
    already-open quoted span."""
    prefix = candidate[:start].rstrip()
    return (bool(_QUOTE_FRAME.search(prefix)) or prefix.endswith(('"', "'", "`"))
            or _inside_quote(candidate[:start]))


def detect_detail(text, exit_code=None):
    """(phrase, kind) when the tail shows the tool's own provider/account limit, else
    None; kind is "account" (the whole tool identity fails) or "quota" (one quota
    group may be exhausted). Same detection rules as detect(); structured non-error
    events are quoted data and never count, and weak signals need an outer error
    context or a failed run."""
    failed = exit_code is not None and exit_code != 0
    for candidate, outer, quoted in _candidates(text):
        if quoted:
            continue
        for patterns, kind in ((_ACCOUNT_RE, "account"), (_QUOTA_STRONG_RE, "quota")):
            for pat in patterns:
                for m in pat.finditer(candidate):
                    if outer or not _quoted(candidate, m.start()):
                        return m.group(0), kind
        if outer or failed:
            for pat in _WEAK_RE:
                for m in pat.finditer(candidate):
                    if outer or not _quoted(candidate, m.start()):
                        return m.group(0), "quota"
    return None


def detect(text, exit_code=None):
    """The matched phrase when the tail shows the tool's own provider/account
    limit, else None. Structured non-error events are quoted data and never
    count; on a plain line a match framed as quoted test/API output is skipped.
    Weak signals otherwise need an outer error context or a failed run."""
    detail = detect_detail(text, exit_code)
    return detail[0] if detail else None


def detect_file(path, exit_code=None):
    """detect() on the last TAIL_CHARS bytes of a log file; None when unreadable."""
    detail = detect_detail_file(path, exit_code)
    return detail[0] if detail else None


def detect_detail_file(path, exit_code=None):
    """detect_detail() on the last TAIL_CHARS bytes of a log file; None when unreadable."""
    try:
        data = Path(path).read_bytes()[-TAIL_CHARS:]
    except (OSError, TypeError):
        return None
    return detect_detail(data.decode("utf-8", "replace"), exit_code)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("logfile")
    ap.add_argument("--exit-code", type=int, default=None,
                    help="the tool's exit code; weak signals need it nonzero or an outer error event")
    a = ap.parse_args()
    hit = detect_file(a.logfile, a.exit_code)
    if hit:
        print(f"limit: {' '.join(hit.split())[:160]}")
        return 0
    print("no limit")
    return 1


if __name__ == "__main__":
    sys.exit(main())
