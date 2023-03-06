import sys
from inspect import cleandoc, getdoc
from typing import Dict, Iterable, Optional, Sequence, Tuple, Union

import pytest
from testfixtures import compare

from numpydoc_decorator import DocumentationError, doc


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
    with pytest.raises(DocumentationError):
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


def test_missing_params():
    with pytest.raises(DocumentationError):
        # noinspection PyUnusedLocal
        @doc(
            summary="A function with simple parameters.",
            # no parameters given at all
        )
        def f(bar, baz):
            pass


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
        baz: str,
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
    baz : str
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


def test_returns_extra_value():
    # here there are more return values documented than there are types
    with pytest.raises(DocumentationError):
        # noinspection PyUnusedLocal
        @doc(
            summary="A function with simple parameters.",
            returns={
                "spam": "Surprisingly healthy.",
                "eggs": "Good on toast.",
            },
        )
        def f() -> str:
            return "dinner"


def test_returns_extra_values():
    # here there are more return values documented than there are types
    with pytest.raises(DocumentationError):
        # noinspection PyUnusedLocal
        @doc(
            summary="A function with simple parameters.",
            returns={
                "spam": "Surprisingly healthy.",
                "eggs": "Good on toast.",
                "toast": "Good with eggs.",
            },
        )
        def f() -> Tuple[str, str]:
            return "spam", "eggs"


def test_returns_extra_type():
    # here there are more return types than return values documented
    with pytest.raises(DocumentationError):
        # noinspection PyUnusedLocal
        @doc(
            summary="A function with simple parameters.",
            returns={
                "spam": "Surprisingly healthy.",
            },
        )
        def f() -> Tuple[str, str]:
            return "spam", "eggs"


def test_returns_extra_types():
    # here there are more return types than return values documented
    with pytest.raises(DocumentationError):
        # noinspection PyUnusedLocal
        @doc(
            summary="A function with simple parameters.",
            returns={
                "spam": "Surprisingly healthy.",
                "eggs": "Good on toast.",
            },
        )
        def f() -> Tuple[str, str, str]:
            return "spam", "eggs", "toast"


def test_deprecation():
    # noinspection PyUnusedLocal
    @doc(
        summary="A deprecated function.",
        deprecation=dict(
            version="1.6.0",
            reason="`ndobj_old` will be removed in NumPy 2.0.0, it is replaced by `ndobj_new` because the latter works also with array subclasses.",  # noqa
        ),
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
    A deprecated function.

    .. deprecated:: 1.6.0
        `ndobj_old` will be removed in NumPy 2.0.0, it is replaced by
        `ndobj_new` because the latter works also with array subclasses.

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


def test_extended_summary():
    # noinspection PyUnusedLocal
    @doc(
        summary="A function worth talking about.",
        extended_summary="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",  # noqa
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
    A function worth talking about.

    Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
    eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad
    minim veniam, quis nostrud exercitation ullamco laboris nisi ut
    aliquip ex ea commodo consequat. Duis aute irure dolor in
    reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla
    pariatur. Excepteur sint occaecat cupidatat non proident, sunt in
    culpa qui officia deserunt mollit anim id est laborum.

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


def test_method():
    class Foo:
        # noinspection PyUnusedLocal
        @doc(
            summary="A method with simple parameters.",
            parameters={
                "bar": "This is very bar.",
                "baz": "This is totally baz.",
            },
            returns={
                "qux": "Amazingly qux.",
            },
        )
        def m(self, bar, baz):
            pass

    foo = Foo()

    expected = cleandoc(
        """
    A method with simple parameters.

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
    actual = getdoc(Foo.m)
    compare(actual, expected)
    actual = getdoc(foo.m)
    compare(actual, expected)


def test_parameter_defaults():
    # noinspection PyUnusedLocal
    @doc(
        summary="A function with parameters and default values.",
        parameters={
            "bar": "This is very bar.",
            "baz": "This is totally baz.",
            "qux": "Amazingly qux.",
            "spam": "Surprisingly healthy.",
            "eggs": "Good on toast.",
        },
    )
    def f(bar, baz="spam", qux=42, spam=True, eggs=None):
        pass

    expected = cleandoc(
        """
    A function with parameters and default values.

    Parameters
    ----------
    bar
        This is very bar.
    baz, default='spam'
        This is totally baz.
    qux, default=42
        Amazingly qux.
    spam, default=True
        Surprisingly healthy.
    eggs, default=None
        Good on toast.

    """
    )
    actual = getdoc(f)
    compare(actual, expected)


def test_parameter_defaults_typed():
    # noinspection PyUnusedLocal
    @doc(
        summary="A function with parameters and default values.",
        parameters={
            "bar": "This is very bar.",
            "baz": "This is totally baz.",
            "qux": "Amazingly qux.",
            "spam": "Surprisingly healthy.",
            "eggs": "Good on toast.",
        },
    )
    def f(
        bar: str,
        baz: str = "spam",
        qux: int = 42,
        spam: bool = True,
        eggs: Optional[Sequence] = None,
    ):
        pass

    if sys.version_info.major == 3 and sys.version_info.minor < 9:
        expected_eggs_type = "Union[Sequence, NoneType]"
    else:
        expected_eggs_type = "Optional[Sequence]"

    expected = cleandoc(
        f"""
    A function with parameters and default values.

    Parameters
    ----------
    bar : str
        This is very bar.
    baz : str, default='spam'
        This is totally baz.
    qux : int, default=42
        Amazingly qux.
    spam : bool, default=True
        Surprisingly healthy.
    eggs : {expected_eggs_type}, default=None
        Good on toast.

    """
    )
    actual = getdoc(f)
    compare(actual, expected)


def test_var_args_kwargs():
    # noinspection PyUnusedLocal
    @doc(
        summary="A function with variable parameters.",
        parameters={
            "bar": "This is very bar.",
            "baz": "This is totally baz.",
            "args": "Anything else you feel like.",
            "kwargs": "Passed through to somewhere else.",
        },
    )
    def f(bar, baz, *args, **kwargs):
        pass

    expected = cleandoc(
        """
    A function with variable parameters.

    Parameters
    ----------
    bar
        This is very bar.
    baz
        This is totally baz.
    *args
        Anything else you feel like.
    **kwargs
        Passed through to somewhere else.

    """
    )
    actual = getdoc(f)
    compare(actual, expected)


def test_var_args_kwargs_names():
    # noinspection PyUnusedLocal
    @doc(
        summary="A function with variable parameters.",
        parameters={
            "bar": "This is very bar.",
            "baz": "This is totally baz.",
            "arguments": "Anything else you feel like.",
            "keyword_arguments": "Passed through to somewhere else.",
        },
    )
    def f(bar, baz, *arguments, **keyword_arguments):
        pass

    expected = cleandoc(
        """
    A function with variable parameters.

    Parameters
    ----------
    bar
        This is very bar.
    baz
        This is totally baz.
    *arguments
        Anything else you feel like.
    **keyword_arguments
        Passed through to somewhere else.

    """
    )
    actual = getdoc(f)
    compare(actual, expected)


def test_keyword_only_args():
    # noinspection PyUnusedLocal
    @doc(
        summary="A function with keyword only args.",
        parameters={
            "bar": "This is very bar.",
            "baz": "This is totally baz.",
            "qux": "Amazingly qux.",
        },
    )
    def f(bar, *, baz, qux):
        pass

    expected = cleandoc(
        """
    A function with keyword only args.

    Parameters
    ----------
    bar
        This is very bar.
    baz
        This is totally baz.
    qux
        Amazingly qux.

    """
    )
    actual = getdoc(f)
    compare(actual, expected)


def test_yields_basic():
    # noinspection PyUnusedLocal
    @doc(
        summary="A function.",
        yields="Amazingly qux.",
    )
    def f():
        yield 42

    # this isn't strictly kosher as numpydoc demands type is always given
    expected = cleandoc(
        """
    A function.

    Yields
    ------
    Amazingly qux.
    """
    )
    actual = getdoc(f)
    compare(actual, expected)


def test_yields_basic_typed_bare():
    # noinspection PyUnusedLocal
    @doc(
        summary="A function.",
        yields="Amazingly qux.",
    )
    def f() -> Iterable:
        yield 42

    expected = cleandoc(
        """
    A function.

    Yields
    ------
    Amazingly qux.
    """
    )
    actual = getdoc(f)
    compare(actual, expected)


def test_yields_basic_typed_iterable():
    # noinspection PyUnusedLocal
    @doc(
        summary="A function.",
        yields="Amazingly qux.",
    )
    def f() -> Iterable[int]:
        yield 42

    expected = cleandoc(
        """
    A function.

    Yields
    ------
    int
        Amazingly qux.
    """
    )
    actual = getdoc(f)
    compare(actual, expected)


def test_yields_named():
    @doc(
        summary="A function.",
        yields={
            "qux": "Amazingly qux.",
        },
    )
    def f():
        return 42

    # this isn't strictly kosher as numpydoc demands type is always given
    expected = cleandoc(
        """
    A function.

    Yields
    ------
    qux
        Amazingly qux.
    """
    )
    actual = getdoc(f)
    compare(actual, expected)


def test_yields_named_typed():
    # noinspection PyUnusedLocal
    @doc(
        summary="A function.",
        yields={
            "qux": "Amazingly qux.",
        },
    )
    def f() -> int:
        return 42

    expected = cleandoc(
        """
    A function.

    Yields
    ------
    qux : int
        Amazingly qux.
    """
    )
    actual = getdoc(f)
    compare(actual, expected)


def test_yields_multi():
    @doc(
        summary="A function.",
        yields={
            "spam": "Very healthy.",
            "eggs": "Good on toast.",
        },
    )
    def f():
        return "hello", 42

    expected = cleandoc(
        """
    A function.

    Yields
    ------
    spam
        Very healthy.
    eggs
        Good on toast.

    """
    )
    actual = getdoc(f)
    compare(actual, expected)


def test_yields_multi_typed():
    @doc(
        summary="A function.",
        yields={
            "spam": "Very healthy.",
            "eggs": "Good on toast.",
        },
    )
    def f() -> Tuple[str, int]:
        return "hello", 42

    expected = cleandoc(
        """
    A function.

    Yields
    ------
    spam : str
        Very healthy.
    eggs : int
        Good on toast.

    """
    )
    actual = getdoc(f)
    compare(actual, expected)


def test_yields_multi_typed_ellipsis():
    @doc(
        summary="A function.",
        yields={
            "spam": "The more the better.",
        },
    )
    def f() -> Tuple[str, ...]:
        return "spam", "spam", "spam", "spam"

    expected = cleandoc(
        """
    A function.

    Yields
    ------
    spam : Tuple[str, ...]
        The more the better.

    """
    )
    actual = getdoc(f)
    compare(actual, expected)


def test_yields_extra_value():
    # here there are more return values documented than there are types
    with pytest.raises(DocumentationError):
        # noinspection PyUnusedLocal
        @doc(
            summary="A function with simple parameters.",
            yields={
                "spam": "Surprisingly healthy.",
                "eggs": "Good on toast.",
            },
        )
        def f() -> str:
            return "dinner"


def test_yields_extra_values():
    # here there are more return values documented than there are types
    with pytest.raises(DocumentationError):
        # noinspection PyUnusedLocal
        @doc(
            summary="A function with simple parameters.",
            yields={
                "spam": "Surprisingly healthy.",
                "eggs": "Good on toast.",
                "toast": "Good with eggs.",
            },
        )
        def f() -> Tuple[str, str]:
            return "spam", "eggs"


def test_yields_extra_type():
    # here there are more return types than return values documented
    with pytest.raises(DocumentationError):
        # noinspection PyUnusedLocal
        @doc(
            summary="A function with simple parameters.",
            yields={
                "spam": "Surprisingly healthy.",
            },
        )
        def f() -> Tuple[str, str]:
            return "spam", "eggs"


def test_yields_extra_types():
    # here there are more return types than return values documented
    with pytest.raises(DocumentationError):
        # noinspection PyUnusedLocal
        @doc(
            summary="A function with simple parameters.",
            yields={
                "spam": "Surprisingly healthy.",
                "eggs": "Good on toast.",
            },
        )
        def f() -> Tuple[str, str, str]:
            return "spam", "eggs", "toast"


# TODO other parameters
# TODO yields section
# TODO yields and returns is an error
# TODO receives section
# TODO raises section
# TODO warns section
# TODO warnings section
# TODO see also section
# TODO notes section
# TODO references section
# TODO examples section
# TODO test numpydoc example
# TODO test some real numpy functions
# TODO README examples, checked via CI somehow
