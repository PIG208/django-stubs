from mypy.errorcodes import ErrorCode

MANAGER_UNTYPED = ErrorCode("misc", "Untyped manager disallowed", "Django")
MANAGER_MISSING = ErrorCode("misc", "Couldn't resolve manager for model", "Django")
