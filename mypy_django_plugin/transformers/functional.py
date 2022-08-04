from typing import Iterable, List, Optional, Union

from mypy.errorcodes import ARG_TYPE, ATTR_DEFINED
from mypy.nodes import MemberExpr
from mypy.plugin import AttributeContext, FunctionContext, MethodSigContext
from mypy.types import AnyType, CallableType, FunctionLike, Instance, Overloaded, TupleType
from mypy.types import Type as MypyType
from mypy.types import TypeOfAny, get_proper_type

from mypy_django_plugin.lib import helpers

SUPPORTED_OPERATOR_MAGIC_METHODS = frozenset(("__lt__", "__add__", "__radd__", "__mod__"))


def _get_resultclasses(
    ctx: Union[AttributeContext, MethodSigContext, FunctionContext],
    args: List[MypyType],
    allow_instance_types: bool = False,
) -> Optional[Iterable[Instance]]:
    """
    Get resultclasses from a list of types in a call to django.utils.functional.lazy
    by verifying that all the given args are valid types.
    Emit an error message and return None when one of the resultclasses is invalid.
    """
    resultclasses: List[Instance] = []
    for pos, resultclass in enumerate(args):
        if allow_instance_types and isinstance(resultclass, Instance):
            resultclasses.append(resultclass)
        elif not (isinstance(resultclass, FunctionLike) and resultclass.is_type_obj()):
            ctx.api.fail(f"Argument {pos + 2} is invalid as a resultclass", ctx.context, code=ARG_TYPE)
            return None
        else:
            resultclasses.append(Instance(resultclass.type_object(), []))
    return resultclasses


def _get_attribute_from_promise(
    ctx: Union[AttributeContext, MethodSigContext], promise_type: Instance, attr_name: str
) -> MypyType:
    # Skip the attribute check when no generic parameter is given
    if len(promise_type.args) == 0:
        return AnyType(TypeOfAny.from_omitted_generics)

    resultclass_typevar = get_proper_type(promise_type.args[0])

    # The resultclasses are contained in the first type argument of Promise as
    # a subtype of TupleType.
    if isinstance(resultclass_typevar, TupleType):
        resultclass_types = resultclass_typevar.items
    elif isinstance(resultclass_typevar, AnyType):
        return AnyType(TypeOfAny.from_another_any, source_any=resultclass_typevar)
    else:
        ctx.api.fail(f"Cannot resolve the resultclasses of Promise", ctx.context)
        return AnyType(TypeOfAny.from_error)

    resultclasses = _get_resultclasses(ctx, resultclass_types, allow_instance_types=True)
    if resultclasses is not None:
        for resultclass in resultclasses:
            if (attr := resultclass.type.get(attr_name)) and attr.type is not None:
                return attr.type

    ctx.api.fail(f"'{ctx.type}' object has no attribute {attr_name!r}", ctx.context, code=ATTR_DEFINED)
    return AnyType(TypeOfAny.from_error)


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
        default_return_type.ret_type, [AnyType(TypeOfAny.from_error), AnyType(TypeOfAny.from_error)]
    )

    # Get resultclasses from the variadic arguments provided by the caller.
    res = _get_resultclasses(ctx, ctx.arg_types[1])
    if res is not None:
        resultclasses: List[MypyType] = list(res)
        typechecker_api = helpers.get_typechecker_api(ctx)
        proxied_callable_ret_type = helpers.reparametrize_instance(
            default_return_type.ret_type, [helpers.make_tuple(typechecker_api, resultclasses), resultclasses[0]]
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


def transform_promise_method_signature(method_name: str, ctx: MethodSigContext) -> FunctionLike:
    assert method_name in SUPPORTED_OPERATOR_MAGIC_METHODS
    assert isinstance(ctx.type, Instance)

    attr = _get_attribute_from_promise(ctx, ctx.type, method_name)
    if isinstance(attr, CallableType):
        # We are skipping the first argument because the operator magic methods
        # on a Promise object is different from those on the resultclasses.
        # The former expects one argument while the latter expects two, where the
        # first argument is actually supplied as the Promise object itself.
        return attr.copy_modified(
            arg_types=attr.arg_types[1:], arg_names=attr.arg_names[1:], arg_kinds=attr.arg_kinds[1:]
        )
    return ctx.default_signature


def resolve_promise_attribute(ctx: AttributeContext) -> MypyType:
    # If the attribute type is already known, we skip calculation below
    if not isinstance(ctx.default_attr_type, AnyType):
        return ctx.default_attr_type

    assert isinstance(ctx.type, Instance)
    assert isinstance(ctx.context, MemberExpr)
    return _get_attribute_from_promise(ctx, ctx.type, ctx.context.name)
