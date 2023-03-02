from inspect import cleandoc, getdoc

import pytest
from testfixtures import compare

from docstring_builder.numpydoc import DocumentationError, doc


def test_params():
    @doc(
        preamble="A function with simple arguments.",
        parameters={
            "bar": "This is very bar.",
            "baz": "This is totally baz.",
        },
        returns={
            "qux": "Amazingly qux.",
        },
    )
    def f(bar, baz):
        pass

    expected = cleandoc(
        """
    A function with simple arguments.

    Parameters
    ----------
    bar
        This is very bar.
    baz
        This is totally baz.

    Returns
    -------
    qux
        Amazingly qux.
    """
    )
    actual = getdoc(f)
    compare(actual, expected)


def test_long_preamble():
    @doc(
        preamble="A function with simple arguments and a very long preamble. Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",  # noqa
        parameters={
            "bar": "This is very bar.",
            "baz": "This is totally baz.",
        },
        returns={
            "qux": "Amazingly qux.",
        },
    )
    def f(bar, baz):
        pass

    expected = cleandoc(
        """
    A function with simple arguments and a very long preamble. Lorem ipsum
    dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor
    incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
    quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea
    commodo consequat. Duis aute irure dolor in reprehenderit in voluptate
    velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint
    occaecat cupidatat non proident, sunt in culpa qui officia deserunt
    mollit anim id est laborum.

    Parameters
    ----------
    bar
        This is very bar.
    baz
        This is totally baz.

    Returns
    -------
    qux
        Amazingly qux.
    """
    )
    actual = getdoc(f)
    compare(actual, expected)


def test_long_param_doc():
    @doc(
        preamble="A function with simple arguments and a very long param doc.",
        parameters={
            "bar": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",  # noqa
            "baz": "This is totally baz.",
        },
        returns={
            "qux": "Amazingly qux.",
        },
    )
    def f(bar, baz):
        pass

    expected = cleandoc(
        """
    A function with simple arguments and a very long param doc.

    Parameters
    ----------
    bar
        Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
        eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad
        minim veniam, quis nostrud exercitation ullamco laboris nisi ut
        aliquip ex ea commodo consequat. Duis aute irure dolor in
        reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla
        pariatur. Excepteur sint occaecat cupidatat non proident, sunt in
        culpa qui officia deserunt mollit anim id est laborum.
    baz
        This is totally baz.

    Returns
    -------
    qux
        Amazingly qux.
    """
    )
    actual = getdoc(f)
    compare(actual, expected)


def test_missing_param():
    with pytest.raises(DocumentationError):

        @doc(
            preamble="A function with simple arguments.",
            parameters={
                "bar": "This is very bar.",
                # baz parameter is missing
            },
            returns={
                "qux": "Amazingly qux.",
            },
        )
        def f(bar, baz):
            pass
