from textwrap import indent, dedent, fill
from inspect import cleandoc


newline = '\n'


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
    preamble=None,
    parameters=None,
    returns=None,
):

    def decorator(f):

        docstring = ""

        # add preamble
        if preamble:
            docstring += para(preamble)
            docstring += newline
            docstring += newline

        # add parameters
        if parameters:
            docstring += "Parameters" + newline
            docstring += "----------" + newline
            docstring += format_parameters(parameters)

        # TODO check parameters against function signature

        if returns:
            docstring += "Returns" + newline
            docstring += "-------" + newline
            docstring += format_parameters(returns)

        # final cleanup
        docstring = cleandoc(docstring)

        f.__doc__ = docstring
        return f

    return decorator
