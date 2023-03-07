from collections.abc import Generator, Iterable, Iterator
from inspect import Parameter, cleandoc, signature
from textwrap import dedent, fill, indent
from typing import Mapping, Optional, Sequence, Union

try:
    # check whether numpy is installed
    import numpy
    from numpy.typing import ArrayLike, DTypeLike
except ImportError:
    numpy = None
    ArrayLike = None
    DTypeLike = None

try:
    from typing import get_args as typing_get_args
    from typing import get_origin as typing_get_origin
except ImportError:
    from typing_extensions import get_args as typing_get_args
    from typing_extensions import get_origin as typing_get_origin


newline = "\n"


class DocumentationError(Exception):
    pass


def punctuate(s):
    if s:
        s = s.strip()
        s = s[0].capitalize() + s[1:]
        if s[-1] not in ".!?:":
            s += "."
    return s


def format_paragraph(s):
    return fill(punctuate(dedent(s.strip(newline)))) + newline


def format_indented_paragraph(s):
    return indent(format_paragraph(s), prefix="    ")


def format_paragraphs(s):
    prep = dedent(s.strip(newline))
    paragraphs = prep.split(newline + newline)
    docstring = ""
    for paragraph in paragraphs:
        if (
            paragraph.startswith(" ")
            or paragraph.startswith("..")
            or paragraph.startswith(">")
            or paragraph.startswith("[")
        ):
            # leave this as-is
            docstring += paragraph + newline + newline
        else:
            # fill
            docstring += fill(punctuate(paragraph)) + newline + newline
    return docstring


def format_indented_paragraphs(s):
    return indent(format_paragraphs(s), prefix="    ")


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

        # add parameter name, accounting for variable parameters
        if param.kind == Parameter.VAR_POSITIONAL:
            # *args
            docstring += "*" + param_name

        elif param.kind == Parameter.VAR_KEYWORD:
            # **kwargs
            docstring += "**" + param_name

        else:
            # standard parameter
            docstring += param_name + " :"

            # handle type annotation
            if param.annotation is not Parameter.empty:
                docstring += " " + format_type(param.annotation)

            # handle default value
            if param.default is not Parameter.empty:
                if param.annotation is not Parameter.empty:
                    docstring += ","
                docstring += " optional"
                if param.default is not None:
                    docstring += f", default: {param.default!r}"

        # add parameter description
        docstring += newline
        param_doc = parameters[param_name]
        docstring += format_indented_paragraphs(param_doc).strip(newline)
        docstring += newline

    return docstring


def format_type(t):
    # This is probably a bit hacky, could be improved.

    if t == type(None):  # noqa
        return "None"

    elif numpy and t == ArrayLike:
        return "array_like"

    elif numpy and t == Optional[ArrayLike]:
        return "array_like or None"

    elif numpy and t == DTypeLike:
        return "data-type"

    elif numpy and t == Optional[DTypeLike]:
        return "data-type or None"

    # special handling for union types
    elif typing_get_origin(t) == Union and typing_get_args(t):
        return " or ".join([format_type(x) for x in typing_get_args(t)])

    elif typing_get_origin(t) == Optional and typing_get_args(t):
        x = typing_get_args(t)[0]
        return format_type(x) + " or None"

    else:
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
        docstring += return_name.strip() + " :"
        if return_type is not Parameter.empty:
            docstring += f" {format_type(return_type)}"
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


def get_send_annotation(sig):
    return_annotation = sig.return_annotation

    if return_annotation is Parameter.empty:
        # no return annotation
        return Parameter.empty

    return_type_origin = typing_get_origin(return_annotation)

    # check return type is compatible with yields
    if return_type_origin is not Generator:
        raise DocumentationError(
            f"return type {return_type_origin!r} is not compatible with receives"
        )

    # extract yield annotation if possible
    return_type_args = typing_get_args(return_annotation)

    if not return_type_args:
        # no yield annotation
        return Parameter.empty

    else:
        send_annotation = return_type_args[1]
        return send_annotation


def format_yields(yields, sig):
    # yields section is basically the same as the returns section, except we
    # need to access the YieldType annotation from within the return annotation
    if isinstance(yields, str):
        return format_returns_unnamed(yields, get_yield_annotation(sig))
    elif isinstance(yields, Mapping):
        return format_returns_named(yields, get_yield_annotation(sig))
    else:
        raise TypeError("yields must be str or Mapping")


def format_receives(receives, sig):
    # receives section is basically the same as the returns section, except we
    # need to access the SendType annotation from within the return annotation
    if isinstance(receives, str):
        return format_returns_unnamed(receives, get_send_annotation(sig))
    elif isinstance(receives, Mapping):
        return format_returns_named(receives, get_send_annotation(sig))
    else:
        raise TypeError("receives must be str or Mapping")


def format_raises(raises):
    docstring = ""
    for error, description in raises.items():
        docstring += error + newline
        docstring += format_indented_paragraph(description)
    return docstring


def format_maybe_code(obj):
    return getattr(obj, "__qualname__", str(obj))


def format_see_also(see_also):
    if isinstance(see_also, str):
        # assume a single function
        return format_maybe_code(see_also).strip() + newline

    elif isinstance(see_also, Sequence):
        # assume a sequence of functions
        docstring = ""
        for item in see_also:
            docstring += format_maybe_code(item).strip() + newline
        return docstring

    elif isinstance(see_also, Mapping):
        # assume functions with descriptions
        docstring = ""
        for name, description in see_also.items():
            docstring += format_maybe_code(name).strip()
            if description:
                docstring += " :"
                if len(description) < 70:
                    docstring += " " + punctuate(description.strip()) + newline
                else:
                    docstring += newline
                    docstring += format_indented_paragraph(description)
            else:
                docstring += newline
        return docstring


def format_references(references):
    docstring = ""
    for ref, desc in references.items():
        docstring += f".. [{ref}] "
        desc = format_indented_paragraph(desc).strip()
        docstring += desc + newline
    return docstring


def doc(
    summary: str,
    deprecation: Optional[Mapping[str, str]] = None,
    extended_summary: Optional[str] = None,
    parameters: Optional[Mapping[str, str]] = None,
    returns: Optional[Union[str, Mapping[str, str]]] = None,
    yields: Optional[Union[str, Mapping[str, str]]] = None,
    receives: Optional[Union[str, Mapping[str, str]]] = None,
    other_parameters: Optional[Mapping[str, str]] = None,
    raises: Optional[Mapping[str, str]] = None,
    warns: Optional[Mapping[str, str]] = None,
    warnings: Optional[str] = None,
    see_also: Optional[Union[str, Sequence[str], Mapping[str, str]]] = None,
    notes: Optional[str] = None,
    references: Optional[Mapping[str, str]] = None,
    examples: Optional[str] = None,
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
        Description of the function arguments and keywords.
    returns : str or Mapping[str, str], optional
        Explanation of the returned values.
    yields : str or Mapping[str, str], optional
        Explanation of the yielded values.
        This is relevant to generators only.
    receives : str or Mapping[str, str], optional
        Explanation of parameters passed to a generator’s `.send()` method.
    other_parameters : Mapping[str, str], optional
        An optional section used to describe infrequently used parameters.
    raises : Mapping[str, str], optional
        An optional section detailing which errors get raised and under what
        conditions.
    warns : Mapping[str, str], optional
        An optional section detailing which warnings get raised and under what
        conditions.
    warnings : str, optional
        An optional section with cautions to the user in free text/reST.
    see_also : str or Sequence[str] or Mapping[str, str], optional
        An optional section used to refer to related code.
    notes : str, optional
        An optional section that provides additional information about the code,
        possibly including a discussion of the algorithm.
    references : Mapping[str, str], optional
        References cited in the Notes section may be listed here.
    examples : str, optional
        An optional section for examples, using the doctest format.

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

    if receives and not yields:
        raise DocumentationError("if receives, must also have yields")

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

        # add receives section
        if receives:
            docstring += "Receives" + newline
            docstring += "--------" + newline
            docstring += format_receives(receives, sig)

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

        # add warnings section
        if warnings:
            docstring += "Warnings" + newline
            docstring += "--------" + newline
            docstring += format_paragraph(warnings)
            docstring += newline

        # add see also section
        if see_also:
            docstring += "See Also" + newline
            docstring += "--------" + newline
            docstring += format_see_also(see_also)
            docstring += newline

        # add notes section
        if notes:
            docstring += "Notes" + newline
            docstring += "-----" + newline
            docstring += format_paragraphs(notes)

        # add references section
        if references:
            docstring += "References" + newline
            docstring += "----------" + newline
            docstring += format_references(references)
            docstring += newline

        # add examples section
        if examples:
            docstring += "Examples" + newline
            docstring += "--------" + newline
            docstring += format_paragraphs(examples)

        # final cleanup
        docstring = newline + cleandoc(docstring) + newline

        f.__doc__ = docstring
        return f

    return decorator
