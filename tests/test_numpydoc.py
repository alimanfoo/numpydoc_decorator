from inspect import cleandoc, getdoc
from typing import Dict, Optional, Sequence, Tuple, Union

import pytest
from testfixtures import compare

from docstring_builder.numpydoc import DocumentationError, doc


def test_basic():
    # noinspection PyUnusedLocal
    @doc(
        summary="A function with simple parameters.",
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
    A function with simple parameters.

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


def test_long_summary():
    # noinspection PyUnusedLocal
    @doc(
        summary="A function with simple parameters and a very long summary. Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",  # noqa
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
    A function with simple parameters and a very long summary. Lorem ipsum
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
    # noinspection PyUnusedLocal
    @doc(
        summary="A function with simple parameters and a very long param doc.",
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
    A function with simple parameters and a very long param doc.

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
    # noinspection PyUnusedLocal
    @doc(
        summary="A function with simple parameters.",
        parameters={
            "bar": "This is very bar.",
            # baz parameter is missing
        },
    )
    def f(bar, baz):
        pass

    expected = cleandoc(
        """
    A function with simple parameters.

    Parameters
    ----------
    bar
        This is very bar.
    baz

    """
    )
    actual = getdoc(f)
    compare(actual, expected)


def test_missing_params():
    # noinspection PyUnusedLocal
    @doc(
        summary="A function with simple parameters.",
        # no parameters given at all
    )
    def f(bar, baz):
        pass

    expected = cleandoc(
        """
    A function with simple parameters.

    Parameters
    ----------
    bar
    baz

    """
    )
    actual = getdoc(f)
    compare(actual, expected)


def test_extra_param():
    with pytest.raises(DocumentationError):
        # noinspection PyUnusedLocal
        @doc(
            summary="A function with simple parameters.",
            parameters={
                "bar": "This is very bar.",
                "baz": "This is totally baz.",
                "spam": "This parameter is not in the signature.",
            },
            returns={
                "qux": "Amazingly qux.",
            },
        )
        def f(bar, baz):
            pass


def test_parameter_order():
    # noinspection PyUnusedLocal
    @doc(
        summary="A function with typed parameters.",
        parameters={
            # given in different order from signature
            "baz": "This is totally baz.",
            "bar": "This is very bar.",
        },
    )
    def f(bar, baz):
        pass

    expected = cleandoc(
        """
    A function with typed parameters.

    Parameters
    ----------
    bar
        This is very bar.
    baz
        This is totally baz.

    """
    )
    actual = getdoc(f)
    compare(actual, expected)


def test_parameter_types():
    # noinspection PyUnusedLocal
    @doc(
        summary="A function with typed parameters.",
        parameters={
            "bar": "This is very bar.",
            "baz": "This is totally baz.",
            "qux": "Many strings.",
            "spam": "Very healthy.",
            "eggs": "Good on toast.",
        },
    )
    def f(
        bar: int,
        baz: Optional[str],  # N.B., this is shorthand for Union
        qux: Sequence[str],
        spam: Union[list, str],
        eggs: Dict[str, Sequence],
    ):
        pass

    expected = cleandoc(
        """
    A function with typed parameters.

    Parameters
    ----------
    bar : int
        This is very bar.
    baz : Union[str, NoneType]
        This is totally baz.
    qux : Sequence[str]
        Many strings.
    spam : Union[list, str]
        Very healthy.
    eggs : Dict[str, Sequence]
        Good on toast.

    """
    )
    actual = getdoc(f)
    compare(actual, expected)


def test_returns_basic():
    # noinspection PyUnusedLocal
    @doc(
        summary="A function.",
        returns="Amazingly qux.",
    )
    def f():
        return 42

    # this isn't strictly kosher as numpydoc demands type is always given
    expected = cleandoc(
        """
    A function.

    Returns
    -------
    Amazingly qux.
    """
    )
    actual = getdoc(f)
    compare(actual, expected)


def test_returns_basic_typed():
    # noinspection PyUnusedLocal
    @doc(
        summary="A function.",
        returns="Amazingly qux.",
    )
    def f() -> int:
        return 42

    expected = cleandoc(
        """
    A function.

    Returns
    -------
    int
        Amazingly qux.
    """
    )
    actual = getdoc(f)
    compare(actual, expected)


def test_returns_named():
    @doc(
        summary="A function.",
        returns={
            "qux": "Amazingly qux.",
        },
    )
    def f():
        return 42

    # this isn't strictly kosher as numpydoc demands type is always given
    expected = cleandoc(
        """
    A function.

    Returns
    -------
    qux
        Amazingly qux.
    """
    )
    actual = getdoc(f)
    compare(actual, expected)


def test_returns_named_typed():
    # noinspection PyUnusedLocal
    @doc(
        summary="A function.",
        returns={
            "qux": "Amazingly qux.",
        },
    )
    def f() -> int:
        return 42

    expected = cleandoc(
        """
    A function.

    Returns
    -------
    qux : int
        Amazingly qux.
    """
    )
    actual = getdoc(f)
    compare(actual, expected)


def test_returns_multi():
    @doc(
        summary="A function.",
        returns={
            "spam": "Very healthy.",
            "eggs": "Good on toast.",
        },
    )
    def f():
        return "hello", 42

    expected = cleandoc(
        """
    A function.

    Returns
    -------
    spam
        Very healthy.
    eggs
        Good on toast.

    """
    )
    actual = getdoc(f)
    compare(actual, expected)


def test_returns_multi_typed():
    @doc(
        summary="A function.",
        returns={
            "spam": "Very healthy.",
            "eggs": "Good on toast.",
        },
    )
    def f() -> Tuple[str, int]:
        return "hello", 42

    expected = cleandoc(
        """
    A function.

    Returns
    -------
    spam : str
        Very healthy.
    eggs : int
        Good on toast.

    """
    )
    actual = getdoc(f)
    compare(actual, expected)


def test_returns_multi_typed_ellipsis():
    @doc(
        summary="A function.",
        returns={
            "spam": "The more the better.",
        },
    )
    def f() -> Tuple[str, ...]:
        return "spam", "spam", "spam", "spam"

    expected = cleandoc(
        """
    A function.

    Returns
    -------
    spam : Tuple[str, ...]
        The more the better.

    """
    )
    actual = getdoc(f)
    compare(actual, expected)
