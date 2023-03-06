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


def format_paragraph(s):
    return fill(dedent(s.strip())) + newline


def format_indented_paragraph(s):
    return indent(format_paragraph(s), prefix="    ")


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
        docstring += format_indented_paragraph(param_doc)

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
        docstring = format_paragraph(returns)
    else:
        # provide the type
        docstring = format_type(return_annotation) + newline
        docstring += format_indented_paragraph(returns)
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
        docstring += format_indented_paragraph(return_doc)
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


def format_raises(raises):
    docstring = ""
    for error, description in raises.items():
        docstring += error + newline
        docstring += format_indented_paragraph(description)
    return docstring


def doc(
    summary: str,
    deprecation: Optional[Mapping[str, str]] = None,
    extended_summary: Optional[str] = None,
    parameters: Optional[Mapping[str, str]] = None,
    returns: Optional[Union[str, Mapping[str, str]]] = None,
    yields: Optional[Union[str, Mapping[str, str]]] = None,
    other_parameters: Optional[Mapping[str, str]] = None,
    raises: Optional[Mapping[str, str]] = None,
    warns: Optional[Mapping[str, str]] = None,
    warnings: Optional[str] = None,
):
    """Provide documentation for a function or method, to be formatted as a
    numpy-style docstring (numpydoc).

    Parameters
    ----------
    summary : str
        A one-line summary that does not use variable names or the function name.
    deprecation : Mapping[str, str], optional
        Warn users that the object is deprecated. Should include `version` and
        `reason` keys.
    extended_summary : str, optional
        A few sentences giving an extended description.
    parameters : Mapping[str, str], optional
        Description of the function arguments and keywords. Note that types will
        be obtained from the function's type annotations and do not need to be
        provided here.
    returns : str or Mapping[str, str], optional
        Explanation of the returned values. Note that types will be obtained from
        the function's return annotation and do not need to be provided here.
    yields : str or Mapping[str, str], optional
        Explanation of the yielded values. Note that types will be obtained from
        the function's return annotation and do not need to be provided here.
        This is relevant to generators only.
    other_parameters : Mapping[str, str], optional
        An optional section used to describe infrequently used parameters. It
        should only be used if a function has a large number of keyword
        parameters, to prevent cluttering the Parameters section.
    raises : Mapping[str, str], optional
        An optional section detailing which errors get raised and under what
        conditions.
    warns : Mapping[str, str], optional
        An optional section detailing which warnings get raised and under what
        conditions.
    warnings : str, optional
        An optional section with cautions to the user in free text/reST.

    Returns
    -------
    decorator
        A decorator function which can be applied to a function that you want
        to document.

    Raises
    ------
    DocumentationError
        An error is raised if there are any problems with the provided documentation,
        such as missing parameters or parameters not consistent with the
        function's type annotations.

    """
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

        # add summary
        if summary:
            docstring += format_paragraph(summary)
            docstring += newline

        # add deprecation warning
        if deprecation:
            docstring += f".. deprecated:: {deprecation['version']}" + newline
            docstring += format_indented_paragraph(deprecation["reason"])
            docstring += newline

        # add extended summary
        if extended_summary:
            docstring += format_paragraph(extended_summary)
            docstring += newline

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

        # add raises section
        if raises:
            docstring += "Raises" + newline
            docstring += "------" + newline
            docstring += format_raises(raises)
            docstring += newline

        # add warns section
        if warns:
            docstring += "Warns" + newline
            docstring += "-----" + newline
            docstring += format_raises(warns)
            docstring += newline

        if warnings:
            docstring += "Warnings" + newline
            docstring += "--------" + newline
            docstring += format_paragraph(warnings)
            docstring += newline

        # final cleanup
        docstring = cleandoc(docstring)

        f.__doc__ = docstring
        return f

    return decorator
