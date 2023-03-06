from collections.abc import Iterable
from inspect import Parameter, cleandoc, signature
from textwrap import dedent, fill, indent
from typing import Generator, Iterator, Mapping, Optional, Union

try:
    from typing import get_args as typing_get_args
    from typing import get_origin as typing_get_origin
except ImportError:
    from typing_extensions import get_args as typing_get_args
    from typing_extensions import get_origin as typing_get_origin


newline = "\n"


class DocumentationError(Exception):
    pass


def para(s):
    return fill(dedent(s.strip())) + newline


def indent_para(s):
    return indent(para(s), prefix="    ")


def format_parameters(parameters, sig):
    docstring = ""
    # display parameters in order given in function signature
    for param_name, param in sig.parameters.items():
        if param_name == "self":
            # assume this is a method, don't document self parameter
            continue

        # add markers for variable parameters
        if param.kind == Parameter.VAR_POSITIONAL:
            docstring += "*"
        elif param.kind == Parameter.VAR_KEYWORD:
            docstring += "**"

        # add parameter name
        docstring += param_name

        # handle type annotation
        if param.annotation is not Parameter.empty:
            docstring += f" : {format_type(param.annotation)}"

        # handle default value
        if param.default is not Parameter.empty:
            docstring += f", default={param.default!r}"

        # add parameter description
        docstring += newline
        param_doc = parameters[param_name]
        docstring += indent_para(param_doc)

    return docstring


def format_type(t):
    # This is probably a bit hacky, could be improved.
    s = repr(t)
    if s.startswith("<class"):
        s = t.__name__
    s = s.replace("typing.", "")
    return s


def format_returns(returns, sig):
    if isinstance(returns, str):
        return format_returns_simple(returns, sig)
    elif isinstance(returns, Mapping):
        return format_returns_named(returns, sig)
    else:
        raise TypeError("returns must be str or Mapping")


def format_returns_simple(returns, sig):
    return_type = sig.return_annotation
    if return_type is Parameter.empty:
        # just assume it's a description of the return value
        docstring = para(returns)
    else:
        # provide the type
        docstring = format_type(return_type) + newline
        docstring += indent_para(returns)
    docstring += newline
    return docstring


def format_returns_named(returns, sig):
    docstring = ""
    return_annotation = sig.return_annotation

    # handle possibility of multiple return values
    if typing_get_origin(return_annotation) is tuple:
        typing_args = typing_get_args(return_annotation)
        if Ellipsis in typing_args:
            # treat as a single return value
            return_types = [return_annotation]
        else:
            # treat as multiple return values
            return_types = typing_args
    elif return_annotation is Parameter.empty:
        # trust the documentation regarding number of return values
        return_types = [Parameter.empty] * len(returns)
    else:
        # assume a single return value
        return_types = [return_annotation]

    if len(returns) > len(return_types):
        raise DocumentationError("more return values documented than types")

    if len(returns) < len(return_types):
        raise DocumentationError("more return types than values documented")

    for (return_name, return_doc), return_type in zip(returns.items(), return_types):
        docstring += return_name.strip()
        if return_type is not Parameter.empty:
            docstring += f" : {format_type(return_type)}"
        docstring += newline
        docstring += indent_para(return_doc)
    docstring += newline

    return docstring


def format_yields(yields, sig):
    if isinstance(yields, str):
        return format_yields_simple(yields, sig)
    elif isinstance(yields, Mapping):
        return format_yields_named(yields, sig)
    else:
        raise TypeError("yields must be str or Mapping")


def format_yields_simple(yields, sig):
    return_type = sig.return_annotation
    if return_type is Parameter.empty:
        # just assume it's a description of the return value
        docstring = para(yields)
    else:
        # check the type is compatible with yields
        return_type_origin = typing_get_origin(return_type)
        if return_type_origin not in [Generator, Iterator, Iterable]:
            # TODO test this
            raise DocumentationError(
                f"return annotation {return_type_origin!r} is not compatible with yields"
            )

        # provide the inner type
        yield_types = typing_get_args(return_type)

        # add yield type information
        if len(yield_types) == 0:
            # no inner type information
            docstring = para(yields)

        elif len(yield_types) == 1:
            yield_type = yield_types[0]
            docstring = format_type(yield_type) + newline
            docstring += indent_para(yields)

        elif len(yield_types) > 1:
            # TODO test this
            docstring = (
                f"({', '.join([format_type(t) for t in yield_types])})" + newline
            )
            docstring += indent_para(yields)

    docstring += newline
    return docstring


def format_yields_named(yields, sig):
    docstring = ""
    return_annotation = sig.return_annotation

    # handle possibility of multiple return values
    if typing_get_origin(return_annotation) is tuple:
        typing_args = typing_get_args(return_annotation)
        if Ellipsis in typing_args:
            # treat as a single return value
            return_types = [return_annotation]
        else:
            # treat as multiple return values
            return_types = typing_args
    elif return_annotation is Parameter.empty:
        # trust the documentation regarding number of return values
        return_types = [Parameter.empty] * len(yields)
    else:
        # assume a single return value
        return_types = [return_annotation]

    if len(yields) > len(return_types):
        raise DocumentationError("more return values documented than types")

    if len(yields) < len(return_types):
        raise DocumentationError("more return types than values documented")

    for (return_name, return_doc), return_type in zip(yields.items(), return_types):
        docstring += return_name.strip()
        if return_type is not Parameter.empty:
            docstring += f" : {format_type(return_type)}"
        docstring += newline
        docstring += indent_para(return_doc)
    docstring += newline

    return docstring


def doc(
    summary: str = None,
    deprecation: Optional[Mapping[str, str]] = None,
    extended_summary: Optional[str] = None,
    parameters: Optional[Mapping[str, str]] = None,
    returns: Optional[Union[str, Mapping[str, str]]] = None,
    yields: Optional[Union[str, Mapping[str, str]]] = None,
):
    if parameters is None:
        parameters = dict()

    def decorator(f):
        docstring = ""

        # add summary
        if summary:
            docstring += para(summary)
            docstring += newline

        # add deprecation warning
        if deprecation:
            docstring += f".. deprecated:: {deprecation['version']}" + newline
            docstring += indent_para(deprecation["reason"])
            docstring += newline

        # add extended summary
        if extended_summary:
            docstring += para(extended_summary)
            docstring += newline

        # check parameters against function signature
        sig = signature(f)
        for e in sig.parameters:
            if e != "self" and e not in parameters:
                raise DocumentationError(f"Parameter {e} not documented.")
        for g in parameters:
            if g not in sig.parameters:
                raise DocumentationError(
                    f"Parameter {g} not found in function signature."
                )

        # add parameters section
        if sig.parameters:
            docstring += "Parameters" + newline
            docstring += "----------" + newline
            docstring += format_parameters(parameters, sig)
            docstring += newline

        # add returns section
        if returns:
            docstring += "Returns" + newline
            docstring += "-------" + newline
            docstring += format_returns(returns, sig)

        # add yields section
        if yields:
            docstring += "Yields" + newline
            docstring += "------" + newline
            docstring += format_yields(yields, sig)

        # TODO receives

        # TODO raises

        # TODO warns

        # TODO warnings

        # TODO see also

        # TODO notes

        # TODO references

        # TODO examples

        # final cleanup
        docstring = cleandoc(docstring)

        f.__doc__ = docstring
        return f

    return decorator
