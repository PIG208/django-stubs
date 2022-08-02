from typing import Iterable, List, Optional

from mypy.errorcodes import ARG_TYPE
from mypy.plugin import AttributeContext, FunctionContext
from mypy.types import AnyType, CallableType, FunctionLike, Instance, Overloaded
from mypy.types import Type as MypyType
from mypy.types import TypeOfAny, get_proper_type

from mypy_django_plugin.lib import helpers


def _get_resultclasses(ctx: FunctionContext, args: List[MypyType]) -> Optional[Iterable[Instance]]:
    """
    Get resultclasses from a list of types in a call to django.utils.functional.lazy
    by verifying that all the given args are valid types.
    Emit an error message and return None when one of the resultclasses is invalid.
    """
    resultclasses: List[Instance] = []
    for pos, resultclass in enumerate(args):
        if not (isinstance(resultclass, FunctionLike) and resultclass.is_type_obj()):
            ctx.api.fail(f"Argument {pos + 2} is invalid as a resultclass", ctx.context, code=ARG_TYPE)
            return None
        resultclasses.append(Instance(resultclass.type_object(), []))
    return resultclasses


def get_lazy_return_type(ctx: FunctionContext) -> MypyType:
    # The default return type should be transformed to
    # a function that returns a Promise object.
    default_return_type = get_proper_type(ctx.default_return_type)
    assert isinstance(default_return_type, CallableType)
    assert isinstance(default_return_type.ret_type, Instance)

    # The possibly overloaded function to be proxied.
    # We do preserve the signature(s), but all the return types are
    # substituted with Promise[_ResultClassT] unconditionally.
    # TODO: Perform compatibility check with the original return types.
    proxied_callable_type = get_proper_type(ctx.arg_types[0][0])
    # Fall back to django.utils.functional.Promise[Any] when
    # resultclasses is invalid
    proxied_callable_ret_type = helpers.reparametrize_instance(
        default_return_type.ret_type, [AnyType(TypeOfAny.from_error)]
    )

    # Get resultclasses from the variadic arguments provided by the caller.
    res = _get_resultclasses(ctx, ctx.arg_types[1])
    if res is not None:
        resultclasses: List[MypyType] = list(res)
        typechecker_api = helpers.get_typechecker_api(ctx)
        proxied_callable_ret_type = helpers.reparametrize_instance(
            default_return_type.ret_type, [helpers.make_tuple(typechecker_api, resultclasses)]
        )

    if isinstance(proxied_callable_type, CallableType):
        return proxied_callable_type.copy_modified(
            ret_type=proxied_callable_ret_type,
        )
    elif isinstance(proxied_callable_type, Overloaded):
        return Overloaded(
            [callable.copy_modified(ret_type=proxied_callable_ret_type) for callable in proxied_callable_type.items]
        )
    else:
        return default_return_type.copy_modified(ret_type=proxied_callable_ret_type)


def resolve_promise_method(ctx: AttributeContext) -> MypyType:
    return AnyType(TypeOfAny.from_error)
