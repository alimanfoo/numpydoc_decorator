from collections.abc import Mapping
from inspect import Parameter, cleandoc, signature
from textwrap import dedent, fill, indent

newline = "\n"


class DocumentationError(Exception):
    pass


def para(s):
    return fill(dedent(s.strip()))


def indent_para(s):
    return indent(para(s), prefix="    ")


def format_parameters(parameters, sig):
    docstring = ""
    # display parameters in order given in function signature
    for param_name, param in sig.parameters.items():
        param_doc = parameters[param_name]
        docstring += param_name.strip()
        if param.annotation is not Parameter.empty:
            docstring += f" : {format_annotation(param.annotation)}"
        docstring += newline
        docstring += indent_para(param_doc)
        docstring += newline
    docstring += newline
    return docstring


def format_annotation(t):
    # This is probably a bit hacky, could be improved.
    s = repr(t)
    if s.startswith("<class"):
        s = t.__name__
    s = s.replace("typing.", "")
    return s


def format_returns(returns, sig):
    docstring = ""
    for param_name, param_doc in returns.items():
        docstring += param_name.strip()
        docstring += newline
        docstring += indent_para(param_doc)
        docstring += newline
    docstring += newline
    return docstring


def doc(
    summary: str = None,
    parameters: Mapping = None,
    returns: Mapping = None,
):
    def decorator(f):
        docstring = ""

        # add summary
        if summary:
            docstring += para(summary)
            docstring += newline
            docstring += newline

        # check parameters against function signature
        # TODO strict=False generate docs for missing params
        sig = signature(f)
        expected_param_names = list(sig.parameters)
        given_param_names = list(parameters) if parameters else []
        for e in expected_param_names:
            if e not in given_param_names:
                raise DocumentationError(f"Parameter {e} not documented.")
        for g in given_param_names:
            if g not in expected_param_names:
                raise DocumentationError(
                    f"Parameter {g} not found in function signature."
                )

        if parameters:
            docstring += "Parameters" + newline
            docstring += "----------" + newline
            docstring += format_parameters(parameters, sig)

        if returns:
            docstring += "Returns" + newline
            docstring += "-------" + newline
            docstring += format_returns(returns, sig)

        # final cleanup
        docstring = cleandoc(docstring)

        f.__doc__ = docstring
        return f

    return decorator
