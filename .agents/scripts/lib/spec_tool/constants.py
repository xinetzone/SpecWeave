import re

_REQ_SEC_RE = re.compile(r"^##\s+(ADDED|MODIFIED|REMOVED)\s+Requirements?", re.IGNORECASE)
_REQ_HDR_RE = re.compile(r"^###\s+Requirement:\s+(.+)")
_SCN_HDR_RE = re.compile(r"^####\s+Scenario:\s+(.+)")

__all__ = ["_REQ_SEC_RE", "_REQ_HDR_RE", "_SCN_HDR_RE"]
