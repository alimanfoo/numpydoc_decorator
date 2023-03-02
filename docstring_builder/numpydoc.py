from collections.abc import Mapping
from inspect import cleandoc, signature
from textwrap import dedent, fill, indent

newline = "\n"


class DocumentationError(Exception):
    pass


def para(s):
    return fill(dedent(s.strip()))


def indent_para(s):
    return indent(para(s), prefix="    ")


def format_parameters(parameters):
    docstring = ""
    for param_name, param_doc in parameters.items():
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
            docstring += format_parameters(parameters)

        if returns:
            docstring += "Returns" + newline
            docstring += "-------" + newline
            docstring += format_parameters(returns)

        # final cleanup
        docstring = cleandoc(docstring)

        f.__doc__ = docstring
        return f

    return decorator
