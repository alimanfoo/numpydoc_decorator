from collections.abc import Generator, Iterable, Iterator, Sequence
from inspect import Parameter, Signature, cleandoc, signature
from textwrap import dedent, fill, indent
from typing import Callable, Dict, List, Mapping, Optional
from typing import Sequence as SequenceType
from typing import Tuple, Union

from typing_extensions import Annotated, Literal
from typing_extensions import get_args as typing_get_args
from typing_extensions import get_origin as typing_get_origin
from typing_extensions import get_type_hints

NoneType = type(None)

try:
    # check whether numpy is installed
    import numpy
    from numpy.typing import ArrayLike, DTypeLike
except ImportError:
    # numpy is optional, this package should still work if not installed
    numpy = None  # type: ignore
    ArrayLike = None  # type: ignore
    DTypeLike = None  # type: ignore


newline = "\n"


class DocumentationError(Exception):
    pass


def punctuate(s: str):
    # This is possibly controversial, should we be enforcing punctuation? Will
    # do so for now, as it is easy to forget a full stop at the end of a
    # piece of documentation, but looks better if punctuation is consistent.
    if s:
        s = s.strip()
        s = s[0].capitalize() + s[1:]
        if s[-1] not in ".!?:":
            s += "."
    return s


def format_paragraph(s: str):
    return fill(punctuate(dedent(s.strip(newline)))) + newline


def format_indented_paragraph(s: str):
    return indent(format_paragraph(s), prefix="    ")


def format_paragraphs(s: str):
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


def format_indented_paragraphs(s: str):
    return indent(format_paragraphs(s), prefix="    ")


def format_parameters(parameters: Mapping[str, str], sig: Signature):
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
    t_orig = typing_get_origin(t)
    t_args = typing_get_args(t)

    if t == NoneType:
        return "None"

    elif numpy and t == ArrayLike:
        return "array_like"

    elif numpy and t == Optional[ArrayLike]:
        return "array_like or None"

    elif numpy and t == DTypeLike:
        return "data-type"

    elif numpy and t == Optional[DTypeLike]:
        return "data-type or None"

    # special handling for annotated types
    elif t_orig == Annotated:
        x = t_args[0]
        return format_type(x)

    # special handling for union types
    elif t_orig == Union and t_args:
        return " or ".join([format_type(x) for x in t_args])

    elif t_orig == Optional and t_args:
        x = t_args[0]
        return format_type(x) + " or None"

    # humanize Literal types
    elif t_orig == Literal and t_args:
        return "{" + ", ".join([repr(i) for i in t_args]) + "}"

    # humanize sequence types
    elif t_orig in [list, List, Sequence, SequenceType] and t_args:
        x = t_args[0]
        return format_type(t_orig).lower() + " of " + format_type(x)

    # humanize variable length tuples
    elif t_orig in [tuple, Tuple] and t_args and Ellipsis in t_args:
        x = t_args[0]
        return "tuple of " + format_type(x)

    else:
        s = repr(t)
        # deal with built-in classes like int, etc.
        if s.startswith("<class"):
            s = t.__name__
        s = s.replace("typing.", "")
        return s


def format_returns(returns: Union[str, bool, Mapping[str, str]], sig: Signature):
    if returns is True:
        return format_returns_auto(sig.return_annotation)
    if isinstance(returns, str):
        return format_returns_unnamed(returns, sig.return_annotation)
    elif isinstance(returns, Mapping):
        return format_returns_named(returns, sig.return_annotation)
    else:
        raise TypeError("returns must be str or Mapping")


def format_returns_auto(return_annotation):
    assert return_annotation is not Parameter.empty
    docstring = format_type(return_annotation) + newline
    return docstring


def format_returns_unnamed(returns: str, return_annotation):
    if return_annotation is Parameter.empty:
        # just assume it's a description of the return value
        docstring = format_paragraph(returns)
    else:
        # provide the type
        docstring = format_type(return_annotation) + newline
        docstring += format_indented_paragraph(returns)
    docstring += newline
    return docstring


def format_returns_named(returns: Mapping[str, str], return_annotation):
    docstring = ""

    if return_annotation is Parameter.empty:
        # trust the documentation regarding number of return values
        return_types = (Parameter.empty,) * len(returns)

    # handle possibility of multiple return values
    elif typing_get_origin(return_annotation) in [tuple, Tuple]:
        return_type_args = typing_get_args(return_annotation)
        if return_type_args and Ellipsis not in return_type_args:
            # treat as multiple return values
            return_types = return_type_args
        else:
            # treat as a single return value
            return_types = (return_annotation,)

    else:
        # assume a single return value
        return_types = (return_annotation,)

    if len(returns) > len(return_types):
        raise DocumentationError(
            f"more values documented {list(returns)} than types {return_types}"
        )

    if len(returns) < len(return_types):
        raise DocumentationError(
            f"more types {return_types} than values documented {list(returns)}"
        )

    for (return_name, return_doc), return_type in zip(returns.items(), return_types):
        if return_type is Parameter.empty:
            docstring += return_name.strip() + " :"
        else:
            if isinstance(return_name, str):
                docstring += return_name.strip() + " : "
            docstring += format_type(return_type)
        docstring += newline
        if isinstance(return_doc, str):
            docstring += format_indented_paragraph(return_doc)
    docstring += newline

    return docstring


def get_yield_annotation(sig: Signature):
    return_annotation = sig.return_annotation

    if return_annotation is Parameter.empty:
        # no return annotation
        return Parameter.empty

    ret_orig = typing_get_origin(return_annotation)

    # check return type is compatible with yields
    if ret_orig not in [Generator, Iterator, Iterable]:
        raise DocumentationError(
            f"return type {ret_orig!r} is not compatible with yields"
        )

    # extract yield annotation if possible
    ret_args = typing_get_args(return_annotation)

    if not ret_args:
        # no yield annotation
        return Parameter.empty

    else:
        yield_annotation = ret_args[0]
        return yield_annotation


def get_send_annotation(sig: Signature):
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


def format_yields(yields: Union[str, Mapping[str, str]], sig: Signature):
    # yields section is basically the same as the returns section, except we
    # need to access the YieldType annotation from within the return annotation
    if isinstance(yields, str):
        return format_returns_unnamed(yields, get_yield_annotation(sig))
    elif isinstance(yields, Mapping):
        return format_returns_named(yields, get_yield_annotation(sig))
    else:
        raise TypeError("yields must be str or Mapping")


def format_receives(receives: Union[str, Mapping[str, str]], sig: Signature):
    # receives section is basically the same as the returns section, except we
    # need to access the SendType annotation from within the return annotation
    if isinstance(receives, str):
        return format_returns_unnamed(receives, get_send_annotation(sig))
    elif isinstance(receives, Mapping):
        return format_returns_named(receives, get_send_annotation(sig))
    else:
        raise TypeError("receives must be str or Mapping")


def format_raises(raises: Mapping[str, str]):
    docstring = ""
    for error, description in raises.items():
        docstring += error + newline
        docstring += format_indented_paragraph(description)
    return docstring


def format_maybe_code(obj):
    return getattr(obj, "__qualname__", str(obj))


def format_see_also(see_also):
    if isinstance(see_also, (list, tuple)):
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

    else:
        # assume a single function
        return format_maybe_code(see_also).strip() + newline


def format_references(references: Mapping[str, str]):
    docstring = ""
    for ref, desc in references.items():
        docstring += f".. [{ref}] "
        desc = format_indented_paragraph(desc).strip()
        docstring += desc + newline
    return docstring


def unpack_optional(t):
    """Unpack an Optional type."""
    t_orig = typing_get_origin(t)
    t_args = typing_get_args(t)
    if t_orig == Optional:
        return t_args[0]
    if t_orig == Union and len(t_args) == 2 and t_args[1] == NoneType:
        # compatibility for PY37
        return t_args[0]
    return t


def get_annotated_doc(t, default=None):
    t_orig = typing_get_origin(t)
    t_args = typing_get_args(t)
    if t_orig == Annotated:
        # assume first annotation provides documentation
        x = t_args[1]
        if isinstance(x, str):
            return x
    return default


def auto_returns(returns, return_annotation):
    ret_orig = typing_get_origin(return_annotation)
    ret_args = typing_get_args(return_annotation)
    ret_multi = ret_orig in (Tuple, tuple) and Ellipsis not in ret_args
    if ret_multi:
        return auto_returns_multi(returns, ret_args)
    else:
        return auto_returns_single(returns, return_annotation)


def auto_returns_single(returns, return_annotation):
    if returns is None:
        returns_doc = get_annotated_doc(return_annotation, True)
    else:
        returns_doc = returns
    return returns_doc


def auto_returns_multi(returns, ret_args):
    if returns is None:
        # use integers as names for anonymous return values
        returns = tuple(range(len(ret_args)))

    if isinstance(returns, tuple):
        # assume returns_doc provides names for return values
        ret_names = tuple(returns)
        returns_doc = dict()
        for n, t in zip(ret_names, ret_args):
            returns_doc[n] = get_annotated_doc(t, True)

    else:
        returns_doc = returns

    return returns_doc


def _doc(
    summary: str,
    deprecation: Optional[Mapping[str, str]] = None,
    extended_summary: Optional[str] = None,
    parameters: Optional[Mapping[str, str]] = None,
    returns: Optional[Union[str, Tuple[str, ...], Mapping[str, str]]] = None,
    yields: Optional[Union[str, Mapping[str, str]]] = None,
    receives: Optional[Union[str, Mapping[str, str]]] = None,
    other_parameters: Optional[Mapping[str, str]] = None,
    raises: Optional[Mapping[str, str]] = None,
    warns: Optional[Mapping[str, str]] = None,
    warnings: Optional[str] = None,
    see_also: Optional[
        Union[str, SequenceType[str], Mapping[str, Optional[str]]]
    ] = None,
    notes: Optional[str] = None,
    references: Optional[Mapping[str, str]] = None,
    examples: Optional[str] = None,
    include_extras: bool = False,
) -> Callable[[Callable], Callable]:
    # sanity checks
    if returns and yields:
        raise DocumentationError("cannot have both returns and yields")
    if receives and not yields:
        raise DocumentationError("if receives, must also have yields")

    def decorator(f: Callable) -> Callable:
        # set up utility variables
        param_docs: Dict[str, str] = dict()
        if parameters:
            param_docs.update(parameters)
        other_param_docs: Dict[str, str] = dict()
        if other_parameters:
            other_param_docs.update(other_parameters)
        docstring = ""
        sig = signature(f)

        # accommodate use of Annotated types for parameters documentation
        for param_name, param in sig.parameters.items():
            t = unpack_optional(param.annotation)
            param_doc = get_annotated_doc(t)
            if param_doc:
                param_docs.setdefault(param_name, param_doc)

        # accommodate use of Annotated types for returns documentation
        return_annotation = sig.return_annotation
        if (
            return_annotation is not Parameter.empty
            and return_annotation is not None
            and return_annotation != NoneType
            and yields is None
        ):
            returns_doc = auto_returns(returns, return_annotation)
        else:
            returns_doc = returns

        # check for missing parameters
        all_param_docs: Dict[str, str] = dict()
        all_param_docs.update(param_docs)
        all_param_docs.update(other_param_docs)
        for e in sig.parameters:
            if e != "self" and e not in all_param_docs:
                raise DocumentationError(f"Parameter {e} not documented.")

        # N.B., intentionally allow extra parameters which are not in the
        # signature - this can be convenient for the user.

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
        if param_docs:
            docstring += "Parameters" + newline
            docstring += "----------" + newline
            docstring += format_parameters(param_docs, sig)
            docstring += newline

        # add returns section
        if returns_doc:
            docstring += "Returns" + newline
            docstring += "-------" + newline
            docstring += format_returns(returns_doc, sig)

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
        if other_param_docs:
            docstring += "Other Parameters" + newline
            docstring += "----------------" + newline
            docstring += format_parameters(other_param_docs, sig)
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

        # attach the docstring
        f.__doc__ = docstring

        # strip Annotated types, these are unreadable in built-in help() function
        f.__annotations__ = get_type_hints(f, include_extras=include_extras)

        return f

    return decorator


# eat our own dogfood
_docstring = _doc(
    summary="""
        Provide documentation for a function or method, to be formatted as a
        numpy-style docstring (numpydoc).
    """,
    parameters=dict(
        summary="""
            A one-line summary that does not use variable names or the function name.
        """,
        deprecation="""
            Warn users that the object is deprecated. Should include `version` and
            `reason` keys.
        """,
        extended_summary="""
            A few sentences giving an extended description.
        """,
        parameters="""
            Description of the function arguments and keywords.
        """,
        returns="""
            Explanation of the returned values.
        """,
        yields="""
            Explanation of the yielded values. This is relevant to generators only.
        """,
        receives="""
            Explanation of parameters passed to a generator’s `.send()` method.
        """,
        other_parameters="""
            An optional section used to describe infrequently used parameters.
        """,
        raises="""
            An optional section detailing which errors get raised and under what
            conditions.
        """,
        warns="""
            An optional section detailing which warnings get raised and under what
            conditions.
        """,
        warnings="""
            An optional section with cautions to the user in free text/reST.
        """,
        see_also="""
            An optional section used to refer to related code.
        """,
        notes="""
            An optional section that provides additional information about the code,
            possibly including a discussion of the algorithm.
        """,
        references="""
            References cited in the Notes section may be listed here.
        """,
        examples="""
            An optional section for examples, using the doctest format.
        """,
        include_extras="""
            If True, preserve any Annotated types in the annotations on the
            decorated function.
        """,
    ),
    returns="""
        A decorator function which can be applied to a function that you want
        to document.
    """,
    raises=dict(
        DocumentationError="""
            An error is raised if there are any problems with the provided documentation,
            such as missing parameters or parameters not consistent with the
            function's type annotations.
        """
    ),
)
doc = _docstring(_doc)
