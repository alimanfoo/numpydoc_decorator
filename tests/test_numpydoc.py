from inspect import getdoc, cleandoc
from testfixtures import compare

from docstring_builder.numpydoc import doc


@doc(
    preamble="A function with simple arguments.",
    parameters={
        'bar': 'This is very bar.',
        'baz': 'This is totally baz.',
    },
    returns={
        'qux': 'Amazingly qux.',
    }
)
def f1(bar, baz):
    pass


def test_f1():
    expected = cleandoc("""
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
    """)
    actual = getdoc(f1)
    compare(actual, expected)


@doc(
    preamble="A function with simple arguments and a very long preamble. Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",  # noqa
    parameters={
        'bar': 'This is very bar.',
        'baz': 'This is totally baz.',
    },
    returns={
        'qux': 'Amazingly qux.',
    }
)
def f2(bar, baz):
    pass


def test_f2():
    expected = cleandoc("""
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
    """)
    actual = getdoc(f2)
    compare(actual, expected)


@doc(
    preamble="A function with simple arguments and a very long param doc.",
    parameters={
        'bar': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.',  # noqa
        'baz': 'This is totally baz.',
    },
    returns={
        'qux': 'Amazingly qux.',
    }
)
def f3(bar, baz):
    pass


def test_f3():
    expected = cleandoc("""
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
    """)
    actual = getdoc(f3)
    compare(actual, expected)
