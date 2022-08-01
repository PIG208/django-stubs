import functools
import types
from contextlib import ContextDecorator
from typing import Any, Callable, Optional, Type, Union

from django.http.request import HttpRequest
from django.utils.functional import Promise

LANGUAGE_SESSION_KEY: str

class TranslatorCommentWarning(SyntaxWarning): ...

class Trans:
    activate: Callable
    check_for_language: functools._lru_cache_wrapper
    deactivate: Callable
    deactivate_all: Callable
    get_language: Callable
    get_language_bidi: Callable
    get_language_from_path: Callable
    get_language_from_request: Callable
    gettext: Callable
    gettext_noop: Callable
    ngettext: Callable
    npgettext: Callable
    pgettext: Callable
    def __getattr__(self, real_name: Any): ...

def gettext_noop(message: str) -> str: ...
def gettext(message: str) -> str: ...
def ngettext(singular: str, plural: str, number: float) -> str: ...
def pgettext(context: str, message: str) -> str: ...
def npgettext(context: str, singular: str, plural: str, number: int) -> str: ...

# lazy evaluated translation functions
def gettext_lazy(message: str) -> Promise: ...
def pgettext_lazy(context: str, message: str) -> Promise: ...
def ngettext_lazy(singular: str, plural: str, number: Union[int, str, None] = ...) -> Promise: ...
def npgettext_lazy(context: str, singular: str, plural: str, number: Union[int, str, None] = ...) -> Promise: ...

# NOTE: These translation functions are deprecated and removed in Django 4.0. We should remove them when we drop
# support for 3.2
def ugettext_noop(message: str) -> str: ...
def ugettext(message: str) -> str: ...
def ungettext(singular: str, plural: str, number: float) -> str: ...

ugettext_lazy = gettext_lazy
ungettext_lazy = ngettext_lazy

def activate(language: str) -> None: ...
def deactivate() -> None: ...

class override(ContextDecorator):
    language: Optional[str] = ...
    deactivate: bool = ...
    def __init__(self, language: Optional[str], deactivate: bool = ...) -> None: ...
    old_language: Optional[str] = ...
    def __enter__(self) -> None: ...
    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[types.TracebackType],
    ) -> None: ...

def get_language() -> str: ...
def get_language_from_path(path: str) -> Optional[str]: ...
def get_language_bidi() -> bool: ...
def check_for_language(lang_code: Optional[str]) -> bool: ...
def to_language(locale: str) -> str: ...
def to_locale(language: str) -> str: ...
def get_language_from_request(request: HttpRequest, check_path: bool = ...) -> str: ...
def templatize(src: str, **kwargs: Any) -> str: ...
def deactivate_all() -> None: ...
def get_supported_language_variant(lang_code: str, *, strict: bool = ...) -> str: ...
def get_language_info(lang_code: str) -> Any: ...
def trim_whitespace(s: str) -> str: ...
def round_away_from_one(value: int) -> int: ...
