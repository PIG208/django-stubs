import sys
from functools import wraps as wraps  # noqa: F401
from typing import Any, Callable, Generic, List, Optional, Tuple, Type, TypeVar, Union, overload

from django.db.models.base import Model

if sys.version_info < (3, 8):
    from typing_extensions import Protocol
else:
    from typing import Protocol

_T = TypeVar("_T")

class cached_property(Generic[_T]):
    func: Callable[..., _T] = ...
    name: str = ...
    def __init__(self, func: Callable[..., _T], name: str = ...): ...
    @overload
    def __get__(self, instance: None, cls: Type[Any] = ...) -> "cached_property[_T]": ...
    @overload
    def __get__(self, instance: object, cls: Type[Any] = ...) -> _T: ...

_ResultClassT = TypeVar("_ResultClassT", bound=Tuple)
_OperandT = TypeVar("_OperandT")

# Promise is only subclassed by a proxy class defined in the lazy function
# so it makes sense for it to have all the methods available in that proxy class
class Promise(Generic[_ResultClassT, _OperandT]):
    def __init__(self, args: Any, kw: Any) -> None: ...
    def __reduce__(self) -> Tuple[Any, Tuple[Any]]: ...
    def __lt__(self, other: Union[Promise[_ResultClassT, _OperandT], _OperandT]) -> bool: ...
    def __mod__(self, rhs: Union[Promise[_ResultClassT, _OperandT], _OperandT]) -> _OperandT: ...
    def __add__(self, other: Union[Promise[_ResultClassT, _OperandT], _OperandT]) -> _OperandT: ...
    def __radd__(self, other: Union[Promise[_ResultClassT, _OperandT], _OperandT]) -> _OperandT: ...
    def __deepcopy__(self, memo: Any): ...

def lazy(func: Callable[..., Any], *resultclasses: Any) -> Callable[..., Promise]: ...
def lazystr(text: Any) -> Promise[Tuple[str], str]: ...
def keep_lazy(*resultclasses: Any) -> Callable[[Callable[..., Any]], Promise[Any, Any]]: ...
def keep_lazy_text(func: Callable[..., str]) -> Callable[..., Promise[Tuple[str], str]]: ...

empty: object

def new_method_proxy(func: Callable[..., _T]) -> Callable[..., _T]: ...

class LazyObject:
    def __init__(self) -> None: ...
    __getattr__: Callable = ...
    def __setattr__(self, name: str, value: Any) -> None: ...
    def __delattr__(self, name: str) -> None: ...
    def __reduce__(self) -> Tuple[Callable, Tuple[Model]]: ...
    def __copy__(self) -> LazyObject: ...
    __bytes__: Callable = ...
    __bool__: Callable = ...
    __dir__: Callable = ...
    __class__: Any = ...
    __ne__: Callable = ...
    __hash__: Callable = ...
    __getitem__: Callable = ...
    __setitem__: Callable = ...
    __delitem__: Callable = ...
    __iter__: Callable = ...
    __len__: Callable = ...
    __contains__: Callable = ...

def unpickle_lazyobject(wrapped: Model) -> Model: ...

class SimpleLazyObject(LazyObject):
    def __init__(self, func: Callable[[], Any]) -> None: ...
    def __copy__(self) -> SimpleLazyObject: ...

_PartitionMember = TypeVar("_PartitionMember")

def partition(
    predicate: Callable[[_PartitionMember], Union[int, bool]], values: List[_PartitionMember]
) -> Tuple[List[_PartitionMember], List[_PartitionMember]]: ...

_Get = TypeVar("_Get", covariant=True)
_Self = TypeVar("_Self")

class classproperty(Generic[_Get]):
    fget: Optional[Callable[[_Self], _Get]] = ...
    def __init__(self, method: Optional[Callable[[_Self], _Get]] = ...) -> None: ...
    def __get__(self, instance: Optional[_Self], cls: Type[_Self] = ...) -> _Get: ...
    def getter(self, method: Callable[[_Self], _Get]) -> classproperty[_Get]: ...

class _Getter(Protocol[_Get]):
    """Type fake to declare some read-only properties (until `property` builtin is generic)

    We can use something like `Union[_Getter[str], str]` in base class to avoid errors
    when redefining attribute with property or property with attribute.
    """

    @overload
    def __get__(self: _Self, __instance: None, __typeobj: Optional[Type[Any]]) -> _Self: ...
    @overload
    def __get__(self, __instance: Any, __typeobj: Optional[Type[Any]]) -> _Get: ...
