from collections.abc import Generator, Iterable, Iterator
from inspect import Parameter, cleandoc, signature
from textwrap import dedent, fill, indent
from typing import Mapping, Optional, Union

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

        if param_name not in parameters:
            # account for documentation of parameters and other parameters separately
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
        return format_returns_unnamed(returns, sig.return_annotation)
    elif isinstance(returns, Mapping):
        return format_returns_named(returns, sig.return_annotation)
    else:
        raise TypeError("returns must be str or Mapping")


def format_returns_unnamed(returns, return_annotation):
    if return_annotation is Parameter.empty:
        # just assume it's a description of the return value
        docstring = para(returns)
    else:
        # provide the type
        docstring = format_type(return_annotation) + newline
        docstring += indent_para(returns)
    docstring += newline
    return docstring


def format_returns_named(returns, return_annotation):
    docstring = ""

    if return_annotation is Parameter.empty:
        # trust the documentation regarding number of return values
        return_types = [Parameter.empty] * len(returns)

    # handle possibility of multiple return values
    elif typing_get_origin(return_annotation) is tuple:
        return_type_args = typing_get_args(return_annotation)
        if return_type_args and Ellipsis not in return_type_args:
            # treat as multiple return values
            return_types = return_type_args
        else:
            # treat as a single return value
            return_types = [return_annotation]

    else:
        # assume a single return value
        return_types = [return_annotation]

    if len(returns) > len(return_types):
        raise DocumentationError(
            f"more values documented {list(returns)} than types {return_types}"
        )

    if len(returns) < len(return_types):
        raise DocumentationError(
            f"more types {return_types} than values documented {list(returns)}"
        )

    for (return_name, return_doc), return_type in zip(returns.items(), return_types):
        docstring += return_name.strip()
        if return_type is not Parameter.empty:
            docstring += f" : {format_type(return_type)}"
        docstring += newline
        docstring += indent_para(return_doc)
    docstring += newline

    return docstring


def get_yield_annotation(sig):
    return_annotation = sig.return_annotation

    if return_annotation is Parameter.empty:
        # no return annotation
        return Parameter.empty

    return_type_origin = typing_get_origin(return_annotation)

    # check return type is compatible with yields
    if return_type_origin not in [Generator, Iterator, Iterable]:
        raise DocumentationError(
            f"return type {return_type_origin!r} is not compatible with yields"
        )

    # extract yield annotation if possible
    return_type_args = typing_get_args(return_annotation)

    if not return_type_args:
        # no yield annotation
        return Parameter.empty

    else:
        yield_annotation = return_type_args[0]
        return yield_annotation


def format_yields(yields, sig):
    # yields section is basically the same as the returns section, except we
    # need to access the yield annotation from within the return annotation
    if isinstance(yields, str):
        return format_returns_unnamed(yields, get_yield_annotation(sig))
    elif isinstance(yields, Mapping):
        return format_returns_named(yields, get_yield_annotation(sig))
    else:
        raise TypeError("yields must be str or Mapping")


def doc(
    summary: str,
    deprecation: Optional[Mapping[str, str]] = None,
    extended_summary: Optional[str] = None,
    parameters: Optional[Mapping[str, str]] = None,
    returns: Optional[Union[str, Mapping[str, str]]] = None,
    yields: Optional[Union[str, Mapping[str, str]]] = None,
    other_parameters: Optional[Mapping[str, str]] = None,
):
    if parameters is None:
        parameters = dict()
    if other_parameters is None:
        other_parameters = dict()
    all_parameters = dict()
    all_parameters.update(parameters)
    all_parameters.update(other_parameters)

    if returns and yields:
        raise DocumentationError("cannot have both returns and yields")

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
            if e != "self" and e not in all_parameters:
                raise DocumentationError(f"Parameter {e} not documented.")
        for g in parameters:
            if g not in sig.parameters:
                raise DocumentationError(
                    f"Parameter {g} not found in function signature."
                )
        for g in other_parameters:
            if g not in sig.parameters:
                raise DocumentationError(
                    f"Other parameter {g} not found in function signature."
                )

        # add parameters section
        if parameters:
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

        # add other parameters section
        if other_parameters:
            docstring += "Other Parameters" + newline
            docstring += "----------------" + newline
            docstring += format_parameters(other_parameters, sig)
            docstring += newline

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
