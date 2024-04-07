from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from inspect import cleandoc, getdoc
from typing import (
    Dict,
    ForwardRef,
    Generator,
    Iterable,
    Iterator,
    List,
    Optional,
    Sequence,
    Set,
    Tuple,
    Union,
)

import numpy
import pytest
from numpy.typing import ArrayLike, DTypeLike
from numpydoc.docscrape import FunctionDoc
from numpydoc.validate import validate as numpydoc_validate
from testfixtures import compare
from typing_extensions import Annotated, Literal

from numpydoc_decorator import DocumentationError, doc


def validate(f, allow: Optional[Set[str]] = None) -> None:
    # noinspection PyTypeChecker
    report: Mapping = numpydoc_validate(FunctionDoc(f))
    errors = report["errors"]

    # numpydoc validation errors that we will ignore in all cases
    ignored_errors = {
        # Summary should fit in a single line
        "SS06",
        # No extended summary found
        "ES01",
        # Parameter has no type
        "PR04",
        # The first line of the Returns section should contain only the type,
        # unless multiple values are being returned
        "RT02",
        # See Also section not found
        "SA01",
        # Missing description for See Also reference
        "SA04",
        # No examples section found
        "EX01",
    }

    # ignore errors in some specific cases
    if allow:
        ignored_errors.update(allow)

    for code, desc in errors:
        if code not in ignored_errors:
            assert False, (code, desc)


def test_basic():
    # noinspection PyUnusedLocal
    @doc(
        summary="A function with simple parameters.",
        parameters=dict(
            bar="This is very bar.",
            baz="This is totally baz.",
        ),
        returns=dict(
            qux="Amazingly qux.",
        ),
    )
    def foo(bar, baz):
        pass

    expected = cleandoc(
        """
    A function with simple parameters.

    Parameters
    ----------
    bar :
        This is very bar.
    baz :
        This is totally baz.

    Returns
    -------
    qux :
        Amazingly qux.
    """
    )
    actual = getdoc(foo)
    compare(actual, expected)
    validate(foo)


def test_long_summary():
    # noinspection PyUnusedLocal
    @doc(
        summary="A function with simple parameters and a very long summary. Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",  # noqa
        parameters=dict(
            bar="This is very bar.",
            baz="This is totally baz.",
        ),
        returns=dict(
            qux="Amazingly qux.",
        ),
    )
    def foo(bar, baz):
        pass

    expected = cleandoc(
        """
    A function with simple parameters and a very long summary. Lorem ipsum
    dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor
    incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
    quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
    consequat. Duis aute irure dolor in reprehenderit in voluptate velit
    esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat
    cupidatat non proident, sunt in culpa qui officia deserunt mollit anim
    id est laborum.

    Parameters
    ----------
    bar :
        This is very bar.
    baz :
        This is totally baz.

    Returns
    -------
    qux :
        Amazingly qux.
    """
    )
    actual = getdoc(foo)
    compare(actual, expected)
    validate(foo)


def test_long_param_doc():
    # noinspection PyUnusedLocal
    @doc(
        summary="A function with simple parameters and a very long param doc.",
        parameters=dict(
            bar="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",  # noqa
            baz="This is totally baz.",
        ),
        returns=dict(
            qux="Amazingly qux.",
        ),
    )
    def foo(bar, baz):
        pass

    expected = cleandoc(
        """
    A function with simple parameters and a very long param doc.

    Parameters
    ----------
    bar :
        Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
        eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad
        minim veniam, quis nostrud exercitation ullamco laboris nisi ut
        aliquip ex ea commodo consequat. Duis aute irure dolor in
        reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla
        pariatur. Excepteur sint occaecat cupidatat non proident, sunt in
        culpa qui officia deserunt mollit anim id est laborum.
    baz :
        This is totally baz.

    Returns
    -------
    qux :
        Amazingly qux.
    """
    )
    actual = getdoc(foo)
    compare(actual, expected)
    validate(foo)


def test_missing_param():
    with pytest.raises(DocumentationError):
        # noinspection PyUnusedLocal
        @doc(
            summary="A function with simple parameters.",
            parameters=dict(
                bar="This is very bar.",
                # baz parameter is missing
            ),
        )
        def foo(bar, baz):
            pass


def test_missing_params():
    with pytest.raises(DocumentationError):
        # noinspection PyUnusedLocal
        @doc(
            summary="A function with simple parameters.",
            # no parameters given at all
        )
        def foo(bar, baz):
            pass


def test_extra_param():
    # Be relaxed about this, can be convenient because it allows chucking in
    # everything from a bag of parameters, and only those which are in the
    # function signature are used.

    # noinspection PyUnusedLocal
    @doc(
        summary="A function with simple parameters.",
        parameters=dict(
            bar="This is very bar.",
            baz="This is totally baz.",
            spam="This parameter is not in the signature.",
        ),
        returns=dict(
            qux="Amazingly qux.",
        ),
    )
    def foo(bar, baz):
        pass

    expected = cleandoc(
        """
    A function with simple parameters.

    Parameters
    ----------
    bar :
        This is very bar.
    baz :
        This is totally baz.

    Returns
    -------
    qux :
        Amazingly qux.
    """
    )
    actual = getdoc(foo)
    compare(actual, expected)
    validate(foo)


def test_parameters_order():
    # noinspection PyUnusedLocal
    @doc(
        summary="A function with typed parameters.",
        parameters=dict(
            # given in different order from signature
            baz="This is totally baz.",
            bar="This is very bar.",
        ),
    )
    def foo(bar, baz):
        pass

    expected = cleandoc(
        """
    A function with typed parameters.

    Parameters
    ----------
    bar :
        This is very bar.
    baz :
        This is totally baz.

    """
    )
    actual = getdoc(foo)
    compare(actual, expected)
    validate(foo)


def test_parameters_typed():
    # Support use of Annotated to keep type information and
    # documentation together, assuming second argument provides
    # the documentation.

    # noinspection PyUnusedLocal
    @doc(
        summary="A function with typed parameters.",
        parameters=dict(
            bar="This is very bar.",
            baz="This is totally baz.",
            qux="Many values.",
            spam="You'll love it.",
            eggs="Good with spam.",
            bacon="Good with eggs.",
            sausage="Good with bacon.",
            lobster="Good with sausage.",
            thermidor="A type of lobster dish.",
            # other parameters not needed, will be picked up from Annotated type
        ),
    )
    def foo(
        bar: int,
        baz: str,
        qux: Sequence,
        spam: Union[list, str],
        eggs: Dict[str, Sequence],
        bacon: Literal["xxx", "yyy", "zzz"],
        sausage: List[int],
        lobster: Tuple[float, ...],
        thermidor: Sequence[str],
        norwegian_blue: Annotated[str, "This is an ex-parrot."],
        lumberjack_song: Optional[
            Annotated[int, "I sleep all night and I work all day."]
        ],
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
    qux : Sequence
        Many values.
    spam : list or str
        You'll love it.
    eggs : dict[str, Sequence]
        Good with spam.
    bacon : {'xxx', 'yyy', 'zzz'}
        Good with eggs.
    sausage : list of int
        Good with bacon.
    lobster : tuple of float
        Good with sausage.
    thermidor : sequence of str
        A type of lobster dish.
    norwegian_blue : str
        This is an ex-parrot.
    lumberjack_song : int or None
        I sleep all night and I work all day.

    """
    )
    actual = getdoc(foo)
    compare(actual, expected)
    validate(foo)

    # check annotated types are stripped
    compare(foo.__annotations__["norwegian_blue"], str)
    compare(foo.__annotations__["lumberjack_song"], Optional[int])


def test_parameters_all_annotated():
    # Support use of Annotated to keep type information and
    # documentation together, assuming second argument provides
    # the documentation.

    @doc(
        summary="A function with annotated parameters.",
    )
    def foo(
        bar: Annotated[int, "This is very bar."],
        baz: Annotated[str, "This is totally baz."],
        qux: Annotated[Sequence, "Many values."],
        spam: Annotated[Union[list, str], "You'll love it."],
        eggs: Annotated[Dict[str, Sequence], "Good with spam."],
        bacon: Annotated[Literal["xxx", "yyy", "zzz"], "Good with eggs."],
        sausage: Annotated[List[int], "Good with bacon."],
        lobster: Annotated[Tuple[float, ...], "Good with sausage."],
        thermidor: Annotated[Sequence[str], "A type of lobster dish."],
        norwegian_blue: Annotated[str, "This is an ex-parrot."],
        lumberjack_song: Optional[
            Annotated[int, "I sleep all night and I work all day."]
        ],
    ):
        pass

    expected = cleandoc(
        """
    A function with annotated parameters.

    Parameters
    ----------
    bar : int
        This is very bar.
    baz : str
        This is totally baz.
    qux : Sequence
        Many values.
    spam : list or str
        You'll love it.
    eggs : dict[str, Sequence]
        Good with spam.
    bacon : {'xxx', 'yyy', 'zzz'}
        Good with eggs.
    sausage : list of int
        Good with bacon.
    lobster : tuple of float
        Good with sausage.
    thermidor : sequence of str
        A type of lobster dish.
    norwegian_blue : str
        This is an ex-parrot.
    lumberjack_song : int or None
        I sleep all night and I work all day.

    """
    )
    actual = getdoc(foo)
    compare(actual, expected)
    validate(foo)

    # check annotated types are stripped
    expected_annotations = {
        "bar": int,
        "baz": str,
        "qux": Sequence,
        "spam": Union[list, str],
        "eggs": Dict[str, Sequence],
        "bacon": Literal["xxx", "yyy", "zzz"],
        "sausage": List[int],
        "lobster": Tuple[float, ...],
        "thermidor": Sequence[str],
        "norwegian_blue": str,
        "lumberjack_song": Optional[int],
    }
    compare(foo.__annotations__, expected_annotations)


def test_returns_none():
    # noinspection PyUnusedLocal
    @doc(
        summary="A function.",
    )
    def foo() -> None:
        pass

    expected = cleandoc(
        """
    A function.
    """
    )
    actual = getdoc(foo)
    compare(actual, expected)
    validate(foo, allow={"RT03"})


def test_returns_unnamed():
    # noinspection PyUnusedLocal
    @doc(
        summary="A function.",
        returns="Amazingly qux.",
    )
    def foo():
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
    actual = getdoc(foo)
    compare(actual, expected)
    validate(foo, allow={"RT03"})


def test_returns_unnamed_typed():
    # noinspection PyUnusedLocal
    @doc(
        summary="A function.",
        returns="Amazingly qux.",
    )
    def foo() -> int:
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
    actual = getdoc(foo)
    compare(actual, expected)
    validate(foo)


def test_returns_unnamed_typed_auto():
    # noinspection PyUnusedLocal
    @doc(
        summary="A function.",
    )
    def foo() -> int:
        return 42

    expected = cleandoc(
        """
    A function.

    Returns
    -------
    int
    """
    )
    actual = getdoc(foo)
    compare(actual, expected)
    validate(foo, allow={"RT03"})


def test_returns_unnamed_typed_annotated():
    # noinspection PyUnusedLocal
    @doc(
        summary="A function.",
    )
    def foo() -> Annotated[int, "Amazingly qux."]:
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
    actual = getdoc(foo)
    compare(actual, expected)
    validate(foo)

    # check that annotated types have been stripped
    expected_annotations = {"return": int}
    compare(foo.__annotations__, expected_annotations)


def test_returns_unnamed_multi_typed():
    # noinspection PyUnusedLocal
    @doc(
        summary="A function.",
    )
    def foo() -> Tuple[int, str]:
        return 42, "foo"

    expected = cleandoc(
        """
    A function.

    Returns
    -------
    int
    str
    """
    )
    actual = getdoc(foo)
    compare(actual, expected)
    validate(foo, allow=["RT03"])


def test_returns_unnamed_multi_typed_annotated():
    # noinspection PyUnusedLocal
    @doc(
        summary="A function.",
    )
    def foo() -> Tuple[Annotated[int, "The answer."], Annotated[str, "The question."]]:
        return 42, "foo"

    expected = cleandoc(
        """
    A function.

    Returns
    -------
    int
        The answer.
    str
        The question.
    """
    )
    actual = getdoc(foo)
    compare(actual, expected)
    validate(foo)

    # check type annotations are stripped
    expected_annotations = {"return": Tuple[int, str]}
    compare(foo.__annotations__, expected_annotations)


def test_returns_named():
    @doc(
        summary="A function.",
        returns=dict(
            qux="Amazingly qux.",
        ),
    )
    def foo():
        return 42

    # this isn't strictly kosher as numpydoc demands type is always given
    expected = cleandoc(
        """
    A function.

    Returns
    -------
    qux :
        Amazingly qux.
    """
    )
    actual = getdoc(foo)
    compare(actual, expected)
    validate(foo)


def test_returns_named_typed():
    # noinspection PyUnusedLocal
    @doc(
        summary="A function.",
        returns=dict(
            qux="Amazingly qux.",
        ),
    )
    def foo() -> int:
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
    actual = getdoc(foo)
    compare(actual, expected)
    validate(foo)


def test_returns_named_multi():
    @doc(
        summary="A function.",
        returns=dict(
            spam="You'll love it.",
            eggs="Good with spam.",
        ),
    )
    def foo():
        return "hello", 42

    expected = cleandoc(
        """
    A function.

    Returns
    -------
    spam :
        You'll love it.
    eggs :
        Good with spam.

    """
    )
    actual = getdoc(foo)
    compare(actual, expected)
    validate(foo)


def test_returns_named_multi_typed():
    @doc(
        summary="A function.",
        returns=dict(
            spam="You'll love it.",
            eggs="Good with spam.",
        ),
    )
    def foo() -> Tuple[str, int]:
        return "hello", 42

    expected = cleandoc(
        """
    A function.

    Returns
    -------
    spam : str
        You'll love it.
    eggs : int
        Good with spam.

    """
    )
    actual = getdoc(foo)
    compare(actual, expected)
    validate(foo)


def test_returns_named_multi_typed_annotated():
    @doc(
        summary="A function.",
        returns=("spam", "eggs"),
    )
    def foo() -> (
        Tuple[Annotated[str, "You'll love it."], Annotated[int, "Good with spam."]]
    ):
        return "hello", 42

    expected = cleandoc(
        """
    A function.

    Returns
    -------
    spam : str
        You'll love it.
    eggs : int
        Good with spam.

    """
    )
    actual = getdoc(foo)
    compare(actual, expected)
    validate(foo)

    # check type annotations are stripped
    expected_annotations = {"return": Tuple[str, int]}
    compare(foo.__annotations__, expected_annotations)


def test_returns_named_multi_typed_ellipsis():
    @doc(
        summary="A function.",
        returns=dict(
            spam="The more the better.",
        ),
    )
    def foo() -> Tuple[str, ...]:
        return "spam", "spam", "spam", "spam"

    expected = cleandoc(
        """
    A function.

    Returns
    -------
    spam : tuple of str
        The more the better.

    """
    )
    actual = getdoc(foo)
    compare(actual, expected)
    validate(foo)


def test_returns_extra_name():
    # here there are more return values documented than there are types
    with pytest.raises(DocumentationError):
        # noinspection PyUnusedLocal
        @doc(
            summary="A function with simple parameters.",
            returns=dict(
                spam="You'll love it.",
                eggs="Good with spam.",
            ),
        )
        def foo() -> str:
            return "dinner"


def test_returns_extra_names():
    # here there are more return values documented than there are types
    with pytest.raises(DocumentationError):
        # noinspection PyUnusedLocal
        @doc(
            summary="A function with simple parameters.",
            returns=dict(
                spam="You'll love it.",
                eggs="Good with spam.",
                toast="Good with eggs.",
            ),
        )
        def foo() -> Tuple[str, str]:
            return "spam", "eggs"


def test_returns_extra_type():
    # here there are more return types than return values documented
    with pytest.raises(DocumentationError):
        # noinspection PyUnusedLocal
        @doc(
            summary="A function with simple parameters.",
            returns=dict(
                spam="You'll love it.",
            ),
        )
        def foo() -> Tuple[str, str]:
            return "spam", "eggs"


def test_returns_extra_types():
    # here there are more return types than return values documented
    with pytest.raises(DocumentationError):
        # noinspection PyUnusedLocal
        @doc(
            summary="A function with simple parameters.",
            returns=dict(
                spam="You'll love it.",
                eggs="Good with spam.",
            ),
        )
        def foo() -> Tuple[str, str, str]:
            return "spam", "eggs", "toast"


def test_deprecation():
    # noinspection PyUnusedLocal
    @doc(
        summary="A deprecated function.",
        deprecation=dict(
            version="1.6.0",
            reason="`ndobj_old` will be removed in NumPy 2.0.0, it is replaced by `ndobj_new` because the latter works also with array subclasses.",  # noqa
        ),
        parameters=dict(
            bar="This is very bar.",
            baz="This is totally baz.",
        ),
        returns=dict(
            qux="Amazingly qux.",
        ),
    )
    def foo(bar, baz):
        pass

    expected = cleandoc(
        """
    A deprecated function.

    .. deprecated:: 1.6.0
        `ndobj_old` will be removed in NumPy 2.0.0, it is replaced by
        `ndobj_new` because the latter works also with array subclasses.

    Parameters
    ----------
    bar :
        This is very bar.
    baz :
        This is totally baz.

    Returns
    -------
    qux :
        Amazingly qux.
    """
    )
    actual = getdoc(foo)
    compare(actual, expected)
    validate(foo)


def test_extended_summary():
    # noinspection PyUnusedLocal
    @doc(
        summary="A function worth talking about.",
        extended_summary="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",  # noqa
        parameters=dict(
            bar="This is very bar.",
            baz="This is totally baz.",
        ),
        returns=dict(
            qux="Amazingly qux.",
        ),
    )
    def foo(bar, baz):
        pass

    expected = cleandoc(
        """
    A function worth talking about.

    Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod
    tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim
    veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea
    commodo consequat. Duis aute irure dolor in reprehenderit in voluptate
    velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint
    occaecat cupidatat non proident, sunt in culpa qui officia deserunt
    mollit anim id est laborum.

    Parameters
    ----------
    bar :
        This is very bar.
    baz :
        This is totally baz.

    Returns
    -------
    qux :
        Amazingly qux.
    """
    )
    actual = getdoc(foo)
    compare(actual, expected)
    validate(foo)


def test_method():
    class Foo:
        # noinspection PyUnusedLocal
        @doc(
            summary="A method with simple parameters.",
            parameters=dict(
                bar="This is very bar.",
                baz="This is totally baz.",
            ),
            returns=dict(
                qux="Amazingly qux.",
            ),
        )
        def m(self, bar, baz):
            pass

    foo = Foo()

    expected = cleandoc(
        """
    A method with simple parameters.

    Parameters
    ----------
    bar :
        This is very bar.
    baz :
        This is totally baz.

    Returns
    -------
    qux :
        Amazingly qux.
    """
    )
    actual = getdoc(Foo.m)
    compare(actual, expected)
    actual = getdoc(foo.m)
    compare(actual, expected)
    validate(foo.m)


def test_parameters_defaults_untyped():
    # noinspection PyUnusedLocal
    @doc(
        summary="A function with parameters and default values.",
        parameters=dict(
            bar="This is very bar.",
            baz="This is totally baz.",
            qux="Amazingly qux.",
            spam="You'll love it.",
            eggs="Good with spam.",
        ),
    )
    def foo(bar, baz="spam", qux=42, spam=True, eggs=None):
        pass

    expected = cleandoc(
        """
    A function with parameters and default values.

    Parameters
    ----------
    bar :
        This is very bar.
    baz : optional, default: 'spam'
        This is totally baz.
    qux : optional, default: 42
        Amazingly qux.
    spam : optional, default: True
        You'll love it.
    eggs : optional
        Good with spam.

    """
    )
    actual = getdoc(foo)
    compare(actual, expected)
    # not strictly kosher as parameters are untyped
    validate(foo, allow={"PR02"})


def test_parameters_defaults_typed():
    # noinspection PyUnusedLocal
    @doc(
        summary="A function with parameters and default values.",
        parameters=dict(
            bar="This is very bar.",
            baz="This is totally baz.",
            qux="Amazingly qux.",
            spam="You'll love it.",
            eggs="Good with spam.",
        ),
    )
    def foo(
        bar: str,
        baz: str = "spam",
        qux: int = 42,
        spam: bool = True,
        eggs: Optional[Sequence] = None,
    ):
        pass

    expected = cleandoc(
        """
    A function with parameters and default values.

    Parameters
    ----------
    bar : str
        This is very bar.
    baz : str, optional, default: 'spam'
        This is totally baz.
    qux : int, optional, default: 42
        Amazingly qux.
    spam : bool, optional, default: True
        You'll love it.
    eggs : Sequence or None, optional
        Good with spam.

    """
    )
    actual = getdoc(foo)
    compare(actual, expected)
    validate(foo)


def test_var_args_kwargs():
    # noinspection PyUnusedLocal
    @doc(
        summary="A function with variable parameters.",
        parameters=dict(
            bar="This is very bar.",
            baz="This is totally baz.",
            args="Anything else you feel like.",
            kwargs="Passed through to somewhere else.",
        ),
    )
    def foo(bar, baz, *args, **kwargs):
        pass

    expected = cleandoc(
        """
    A function with variable parameters.

    Parameters
    ----------
    bar :
        This is very bar.
    baz :
        This is totally baz.
    *args
        Anything else you feel like.
    **kwargs
        Passed through to somewhere else.

    """
    )
    actual = getdoc(foo)
    compare(actual, expected)
    validate(foo)


def test_var_args_kwargs_names():
    # noinspection PyUnusedLocal
    @doc(
        summary="A function with variable parameters.",
        parameters=dict(
            bar="This is very bar.",
            baz="This is totally baz.",
            arguments="Anything else you feel like.",
            keyword_arguments="Passed through to somewhere else.",
        ),
    )
    def foo(bar, baz, *arguments, **keyword_arguments):
        pass

    expected = cleandoc(
        """
    A function with variable parameters.

    Parameters
    ----------
    bar :
        This is very bar.
    baz :
        This is totally baz.
    *arguments
        Anything else you feel like.
    **keyword_arguments
        Passed through to somewhere else.

    """
    )
    actual = getdoc(foo)
    compare(actual, expected)
    validate(foo)


def test_keyword_only_args():
    # noinspection PyUnusedLocal
    @doc(
        summary="A function with keyword only args.",
        parameters=dict(
            bar="This is very bar.",
            baz="This is totally baz.",
            qux="Amazingly qux.",
        ),
    )
    def foo(bar, *, baz, qux):
        pass

    expected = cleandoc(
        """
    A function with keyword only args.

    Parameters
    ----------
    bar :
        This is very bar.
    baz :
        This is totally baz.
    qux :
        Amazingly qux.

    """
    )
    actual = getdoc(foo)
    compare(actual, expected)
    validate(foo)


def test_yields_unnamed():
    # noinspection PyUnusedLocal
    @doc(
        summary="A function.",
        yields="Amazingly qux.",
    )
    def foo():
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
    actual = getdoc(foo)
    compare(actual, expected)
    validate(foo)


def test_yields_unnamed_typed_bare():
    # noinspection PyUnusedLocal
    @doc(
        summary="A function.",
        yields="Amazingly qux.",
    )
    def foo() -> Iterable:
        yield 42

    expected = cleandoc(
        """
    A function.

    Yields
    ------
    Amazingly qux.
    """
    )
    actual = getdoc(foo)
    compare(actual, expected)
    validate(foo)


@pytest.mark.parametrize("T", [Iterator, Iterable])
def test_yields_unnamed_typed_iterator(T):
    # noinspection PyUnresolvedReferences
    @doc(
        summary="A function.",
        yields="Amazingly qux.",
    )
    def foo() -> T[int]:
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
    actual = getdoc(foo)
    compare(actual, expected)
    validate(foo)


def test_yields_unnamed_typed_generator():
    # noinspection PyUnusedLocal
    @doc(
        summary="A function.",
        yields="Amazingly qux.",
    )
    def foo() -> Generator[int, None, None]:
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
    actual = getdoc(foo)
    compare(actual, expected)
    validate(foo)


def test_yields_named():
    @doc(
        summary="A function.",
        yields=dict(
            bar="This is very bar.",
        ),
    )
    def foo():
        yield 42

    # this isn't strictly kosher as numpydoc demands type is always given
    expected = cleandoc(
        """
    A function.

    Yields
    ------
    bar :
        This is very bar.

    """
    )
    actual = getdoc(foo)
    compare(actual, expected)
    validate(foo)


def test_yields_named_typed():
    # noinspection PyUnusedLocal
    @doc(
        summary="A function.",
        yields=dict(
            bar="This is very bar.",
        ),
    )
    def foo() -> Iterable[int]:
        yield 42

    expected = cleandoc(
        """
    A function.

    Yields
    ------
    bar : int
        This is very bar.

    """
    )
    actual = getdoc(foo)
    compare(actual, expected)
    validate(foo)


def test_yields_named_multi():
    @doc(
        summary="A function.",
        yields=dict(
            spam="You'll love it.",
            eggs="Good with spam.",
        ),
    )
    def foo():
        yield "hello", 42

    expected = cleandoc(
        """
    A function.

    Yields
    ------
    spam :
        You'll love it.
    eggs :
        Good with spam.

    """
    )
    actual = getdoc(foo)
    compare(actual, expected)
    validate(foo)


def test_yields_named_multi_typed():
    @doc(
        summary="A function.",
        yields=dict(
            spam="You'll love it.",
            eggs="Good with spam.",
        ),
    )
    def foo() -> Iterable[Tuple[str, int]]:
        yield "hello", 42

    expected = cleandoc(
        """
    A function.

    Yields
    ------
    spam : str
        You'll love it.
    eggs : int
        Good with spam.

    """
    )
    actual = getdoc(foo)
    compare(actual, expected)
    validate(foo)


def test_yields_named_multi_typed_ellipsis():
    @doc(
        summary="A function.",
        yields=dict(
            spam="The more the better.",
        ),
    )
    def foo() -> Iterable[Tuple[str, ...]]:
        yield "spam", "spam", "spam", "spam"

    expected = cleandoc(
        """
    A function.

    Yields
    ------
    spam : tuple of str
        The more the better.

    """
    )
    actual = getdoc(foo)
    compare(actual, expected)
    validate(foo)


def test_yields_extra_name():
    # here there are more yield values documented than there are types
    with pytest.raises(DocumentationError):
        # noinspection PyUnusedLocal
        @doc(
            summary="A function with simple parameters.",
            yields=dict(
                spam="You'll love it.",
                eggs="Good with spam.",
            ),
        )
        def foo() -> Iterable[str]:
            yield "dinner"


def test_yields_extra_names():
    # here there are more yield values documented than there are types
    with pytest.raises(DocumentationError):
        # noinspection PyUnusedLocal
        @doc(
            summary="A function with simple parameters.",
            yields=dict(
                spam="You'll love it.",
                eggs="Good with spam.",
                toast="Good with eggs.",
            ),
        )
        def foo() -> Iterable[Tuple[str, str]]:
            yield "spam", "eggs"


def test_yields_extra_type():
    # here there are more yield types than yield values documented
    with pytest.raises(DocumentationError):
        # noinspection PyUnusedLocal
        @doc(
            summary="A function with simple parameters.",
            yields=dict(
                spam="You'll love it.",
            ),
        )
        def foo() -> Iterable[Tuple[str, str]]:
            yield "spam", "eggs"


def test_yields_extra_types():
    # here there are more yield types than yield values documented
    with pytest.raises(DocumentationError):
        # noinspection PyUnusedLocal
        @doc(
            summary="A function with simple parameters.",
            yields=dict(
                spam="You'll love it.",
                eggs="Good with spam.",
            ),
        )
        def foo() -> Iterable[Tuple[str, str, str]]:
            yield "spam", "eggs", "toast"


def test_yields_bad_type():
    with pytest.raises(DocumentationError):
        # noinspection PyUnusedLocal
        @doc(
            summary="A function with simple parameters.",
            yields=dict(
                spam="You'll love it.",
            ),
        )
        def foo() -> Tuple[str, str]:
            return "spam", "eggs"


def test_returns_yields():
    with pytest.raises(DocumentationError):
        # noinspection PyUnusedLocal
        @doc(
            summary="A function with simple parameters.",
            returns=dict(
                spam="You'll love it.",
            ),
            yields=dict(
                spam="You'll love it.",
            ),
        )
        def foo() -> Iterable[str]:
            yield "spam"
            yield "eggs"
            yield "toast"


def test_receives_unnamed():
    # noinspection PyUnusedLocal
    @doc(
        summary="A function.",
        yields="Egg, bacon, sausage, and Spam.",
        receives="Lobster thermidor.",
    )
    def foo():
        x = yield 42  # noqa

    # this isn't strictly kosher as numpydoc demands type is always given
    expected = cleandoc(
        """
    A function.

    Yields
    ------
    Egg, bacon, sausage, and Spam.

    Receives
    --------
    Lobster thermidor.

    """
    )
    actual = getdoc(foo)
    compare(actual, expected)
    # receives section not recognised by numpydoc validate
    validate(foo, allow={"GL06", "GL07"})


def test_receives_unnamed_typed_bare():
    # noinspection PyUnusedLocal
    @doc(
        summary="A function.",
        yields="Egg, bacon, sausage, and Spam.",
        receives="Lobster thermidor.",
    )
    def foo() -> Generator:
        x = yield 42  # noqa

    expected = cleandoc(
        """
    A function.

    Yields
    ------
    Egg, bacon, sausage, and Spam.

    Receives
    --------
    Lobster thermidor.

    """
    )
    actual = getdoc(foo)
    compare(actual, expected)
    # receives section not recognised by numpydoc validate
    validate(foo, allow={"GL06", "GL07"})


def test_receives_unnamed_typed():
    # noinspection PyUnusedLocal
    @doc(
        summary="A function.",
        yields="Egg, bacon, sausage, and Spam.",
        receives="Lobster thermidor.",
    )
    def foo() -> Generator[int, float, None]:
        x = yield 42  # noqa

    expected = cleandoc(
        """
    A function.

    Yields
    ------
    int
        Egg, bacon, sausage, and Spam.

    Receives
    --------
    float
        Lobster thermidor.

    """
    )
    actual = getdoc(foo)
    compare(actual, expected)
    # receives section not recognised by numpydoc validate
    validate(foo, allow={"GL06", "GL07"})


def test_receives_named():
    @doc(
        summary="A function.",
        yields=dict(
            bar="This is very bar.",
        ),
        receives=dict(
            baz="This is totally baz.",
        ),
    )
    def foo():
        x = yield 42  # noqa

    # this isn't strictly kosher as numpydoc demands type is always given
    expected = cleandoc(
        """
    A function.

    Yields
    ------
    bar :
        This is very bar.

    Receives
    --------
    baz :
        This is totally baz.

    """
    )
    actual = getdoc(foo)
    compare(actual, expected)
    # receives section not recognised by numpydoc validate
    validate(foo, allow={"GL06", "GL07"})


def test_receives_named_typed():
    # noinspection PyUnusedLocal
    @doc(
        summary="A function.",
        yields=dict(
            bar="This is very bar.",
        ),
        receives=dict(
            baz="This is totally baz.",
        ),
    )
    def foo() -> Generator[int, float, None]:
        x = yield 42  # noqa

    expected = cleandoc(
        """
    A function.

    Yields
    ------
    bar : int
        This is very bar.

    Receives
    --------
    baz : float
        This is totally baz.

    """
    )
    actual = getdoc(foo)
    compare(actual, expected)
    # receives section not recognised by numpydoc validate
    validate(foo, allow={"GL06", "GL07"})


def test_receives_named_multi():
    @doc(
        summary="A function.",
        yields=dict(
            bar="This is very bar.",
            baz="This is totally baz.",
        ),
        receives=dict(
            spam="You'll love it.",
            eggs="Good with spam.",
        ),
    )
    def foo():
        _, _ = yield "hello", 42

    expected = cleandoc(
        """
    A function.

    Yields
    ------
    bar :
        This is very bar.
    baz :
        This is totally baz.

    Receives
    --------
    spam :
        You'll love it.
    eggs :
        Good with spam.

    """
    )
    actual = getdoc(foo)
    compare(actual, expected)
    # receives section not recognised by numpydoc validate
    validate(foo, allow={"GL06", "GL07"})


def test_receives_named_multi_typed():
    @doc(
        summary="A function.",
        yields=dict(
            bar="This is very bar.",
            baz="This is totally baz.",
        ),
        receives=dict(
            spam="You'll love it.",
            eggs="Good with spam.",
        ),
    )
    def foo() -> Generator[Tuple[str, int], Tuple[float, bool], None]:
        _, _ = yield "hello", 42

    expected = cleandoc(
        """
    A function.

    Yields
    ------
    bar : str
        This is very bar.
    baz : int
        This is totally baz.

    Receives
    --------
    spam : float
        You'll love it.
    eggs : bool
        Good with spam.

    """
    )
    actual = getdoc(foo)
    compare(actual, expected)
    # receives section not recognised by numpydoc validate
    validate(foo, allow={"GL06", "GL07"})


def test_receives_named_multi_typed_ellipsis():
    @doc(
        summary="A function.",
        yields=dict(
            spam="The more the better.",
        ),
        receives=dict(eggs="Good with spam."),
    )
    def foo() -> Generator[Tuple[str, ...], Tuple[float, ...], None]:
        _ = yield "spam", "spam", "spam", "spam"  # noqa

    expected = cleandoc(
        """
    A function.

    Yields
    ------
    spam : tuple of str
        The more the better.

    Receives
    --------
    eggs : tuple of float
        Good with spam.

    """
    )
    actual = getdoc(foo)
    compare(actual, expected)
    # receives section not recognised by numpydoc validate
    validate(foo, allow={"GL06", "GL07"})


def test_receives_extra_name():
    # here there are more receive values documented than there are types
    with pytest.raises(DocumentationError):
        # noinspection PyUnusedLocal
        @doc(
            summary="A function with simple parameters.",
            yields=dict(bar="Totally bar."),
            receives=dict(
                spam="You'll love it.",
                eggs="Good with spam.",
            ),
        )
        def foo() -> Generator[str, float, None]:
            x = yield "dinner"  # noqa


def test_receives_extra_names():
    # here there are more yield values documented than there are types
    with pytest.raises(DocumentationError):
        # noinspection PyUnusedLocal
        @doc(
            summary="A function with simple parameters.",
            yields=dict(bar="Totally bar."),
            receives=dict(
                spam="You'll love it.",
                eggs="Good with spam.",
                bacon="Good with eggs.",
            ),
        )
        def foo() -> Generator[int, Tuple[str, str], None]:
            foo, bar = yield 42
            spam, eggs = yield 84


def test_receives_extra_type():
    # here there are more yield types than yield values documented
    with pytest.raises(DocumentationError):
        # noinspection PyUnusedLocal
        @doc(
            summary="A function with simple parameters.",
            yields=dict(bar="Totally bar."),
            receives=dict(
                spam="You'll love it.",
            ),
        )
        def foo() -> Generator[str, Tuple[str, str], None]:
            x = yield "spam"  # noqa


def test_receives_extra_types():
    # here there are more receive types than yield values documented
    with pytest.raises(DocumentationError):
        # noinspection PyUnusedLocal
        @doc(
            summary="A function with simple parameters.",
            yields=dict(bar="Totally bar."),
            receives=dict(
                spam="You'll love it.",
                eggs="Good with spam.",
            ),
        )
        def foo() -> Generator[str, Tuple[str, str, str], None]:
            x = yield "spam"  # noqa


def test_receives_no_yields():
    with pytest.raises(DocumentationError):
        # noinspection PyUnusedLocal
        @doc(
            summary="A function with simple parameters.",
            receives=dict(
                spam="You'll love it.",
            ),
        )
        def foo() -> Generator[str, str, None]:
            x = yield "spam"  # noqa


def test_other_parameters():
    # noinspection PyUnusedLocal
    @doc(
        summary="A function with other parameters.",
        parameters=dict(
            bar="This is very bar.",
            baz="This is totally baz.",
        ),
        other_parameters=dict(
            spam="You'll love it.",
            eggs="Good with spam.",
        ),
        returns=dict(
            qux="Amazingly qux.",
        ),
    )
    def foo(bar, baz, spam, eggs):
        pass

    expected = cleandoc(
        """
    A function with other parameters.

    Parameters
    ----------
    bar :
        This is very bar.
    baz :
        This is totally baz.

    Returns
    -------
    qux :
        Amazingly qux.

    Other Parameters
    ----------------
    spam :
        You'll love it.
    eggs :
        Good with spam.

    """
    )
    actual = getdoc(foo)
    compare(actual, expected)
    validate(foo)


def test_other_parameters_typed():
    # noinspection PyUnusedLocal
    @doc(
        summary="A function with other parameters.",
        parameters=dict(
            bar="This is very bar.",
            baz="This is totally baz.",
        ),
        other_parameters=dict(
            spam="You'll love it.",
            eggs="Good with spam.",
        ),
        returns=dict(
            qux="Amazingly qux.",
        ),
    )
    def foo(bar: int, baz: str, spam: float, eggs: Tuple[int]) -> bool:
        return True

    expected = cleandoc(
        """
    A function with other parameters.

    Parameters
    ----------
    bar : int
        This is very bar.
    baz : str
        This is totally baz.

    Returns
    -------
    qux : bool
        Amazingly qux.

    Other Parameters
    ----------------
    spam : float
        You'll love it.
    eggs : tuple[int]
        Good with spam.

    """
    )
    actual = getdoc(foo)
    compare(actual, expected)
    validate(foo)


def test_extra_other_param():
    # noinspection PyUnusedLocal
    @doc(
        summary="A function with other parameters.",
        parameters=dict(
            bar="This is very bar.",
            baz="This is totally baz.",
        ),
        returns=dict(
            qux="Amazingly qux.",
        ),
        other_parameters=dict(
            spam="You'll love it.",
            eggs="Good with spam.",
        ),
    )
    def foo(bar, baz, spam):
        pass

    expected = cleandoc(
        """
    A function with other parameters.

    Parameters
    ----------
    bar :
        This is very bar.
    baz :
        This is totally baz.

    Returns
    -------
    qux :
        Amazingly qux.

    Other Parameters
    ----------------
    spam :
        You'll love it.

    """
    )
    actual = getdoc(foo)
    compare(actual, expected)
    validate(foo)


def test_missing_other_param():
    with pytest.raises(DocumentationError):
        # noinspection PyUnusedLocal
        @doc(
            summary="A function with simple parameters.",
            parameters=dict(
                bar="This is very bar.",
                baz="This is totally baz.",
            ),
            returns=dict(
                qux="Amazingly qux.",
            ),
            other_parameters=dict(
                spam="You'll love it.",
                # eggs param is missing
            ),
        )
        def foo(bar, baz, spam, eggs):
            pass


def test_raises_warns_warnings():
    # noinspection PyUnusedLocal
    @doc(
        summary="A function with simple parameters.",
        parameters=dict(
            bar="This is very bar.",
            baz="This is totally baz.",
        ),
        returns=dict(
            qux="Amazingly qux.",
        ),
        raises=dict(
            FileNotFoundError="If the file isn't there.",
            OSError="If something really bad goes wrong.",
        ),
        warns=dict(
            UserWarning="If you do something silly.",
            ResourceWarning="If you use too much memory.",
        ),
        warnings="Here be dragons!",
    )
    def foo(bar, baz):
        pass

    expected = cleandoc(
        """
    A function with simple parameters.

    Parameters
    ----------
    bar :
        This is very bar.
    baz :
        This is totally baz.

    Returns
    -------
    qux :
        Amazingly qux.

    Raises
    ------
    FileNotFoundError
        If the file isn't there.
    OSError
        If something really bad goes wrong.

    Warns
    -----
    UserWarning
        If you do something silly.
    ResourceWarning
        If you use too much memory.

    Warnings
    --------
    Here be dragons!

    """
    )
    actual = getdoc(foo)
    compare(actual, expected)
    validate(foo)


def test_see_also_string():
    # noinspection PyUnusedLocal
    @doc(
        summary="A function with simple parameters.",
        parameters=dict(
            bar="This is very bar.",
            baz="This is totally baz.",
        ),
        returns=dict(
            qux="Amazingly qux.",
        ),
        see_also="spam",
    )
    def foo(bar, baz):
        pass

    expected = cleandoc(
        """
    A function with simple parameters.

    Parameters
    ----------
    bar :
        This is very bar.
    baz :
        This is totally baz.

    Returns
    -------
    qux :
        Amazingly qux.

    See Also
    --------
    spam

    """
    )
    actual = getdoc(foo)
    compare(actual, expected)
    validate(foo)


def test_see_also_sequence():
    # noinspection PyUnusedLocal
    @doc(
        summary="A function with simple parameters.",
        parameters=dict(
            bar="This is very bar.",
            baz="This is totally baz.",
        ),
        returns=dict(
            qux="Amazingly qux.",
        ),
        see_also=["spam", "eggs", print],
    )
    def foo(bar, baz):
        pass

    expected = cleandoc(
        """
    A function with simple parameters.

    Parameters
    ----------
    bar :
        This is very bar.
    baz :
        This is totally baz.

    Returns
    -------
    qux :
        Amazingly qux.

    See Also
    --------
    spam
    eggs
    print

    """
    )
    actual = getdoc(foo)
    compare(actual, expected)
    validate(foo)


def test_see_also_mapping():
    # noinspection PyUnusedLocal
    @doc(
        summary="A function with simple parameters.",
        parameters=dict(
            bar="This is very bar.",
            baz="This is totally baz.",
        ),
        returns=dict(
            qux="Amazingly qux.",
        ),
        see_also=dict(
            spam="You'll love it.",
            eggs="Good with spam.",
            bacon=None,
            lobster_thermidor="Aux crevettes with a Mornay sauce, garnished with truffle pâté, brandy, and a fried egg on top, and Spam.",  # noqa
        ),
    )
    def foo(bar, baz):
        pass

    expected = cleandoc(
        """
    A function with simple parameters.

    Parameters
    ----------
    bar :
        This is very bar.
    baz :
        This is totally baz.

    Returns
    -------
    qux :
        Amazingly qux.

    See Also
    --------
    spam : You'll love it.
    eggs : Good with spam.
    bacon
    lobster_thermidor :
        Aux crevettes with a Mornay sauce, garnished with truffle pâté,
        brandy, and a fried egg on top, and Spam.

    """
    )
    actual = getdoc(foo)
    compare(actual, expected)
    validate(foo)


def test_notes():
    # noinspection PyUnusedLocal
    @doc(
        summary="A function with simple parameters.",
        parameters=dict(
            bar="This is very bar.",
            baz="This is totally baz.",
        ),
        returns=dict(
            qux="Amazingly qux.",
        ),
        notes=r"""
            The FFT is a fast implementation of the discrete Fourier transform:

            .. math:: X(e^{j\omega } ) = x(n)e^{ - j\omega n}

            The discrete-time Fourier time-convolution property states that:

            .. math::

                 x(n) * y(n) \Leftrightarrow X(e^{j\omega } )Y(e^{j\omega } )

            Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

            The value of :math:`\omega` is larger than 5.
        """,  # noqa
    )
    def foo(bar, baz):
        pass

    expected = cleandoc(
        r"""
    A function with simple parameters.

    Parameters
    ----------
    bar :
        This is very bar.
    baz :
        This is totally baz.

    Returns
    -------
    qux :
        Amazingly qux.

    Notes
    -----
    The FFT is a fast implementation of the discrete Fourier transform:

    .. math:: X(e^{j\omega } ) = x(n)e^{ - j\omega n}

    The discrete-time Fourier time-convolution property states that:

    .. math::

         x(n) * y(n) \Leftrightarrow X(e^{j\omega } )Y(e^{j\omega } )

    Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
    eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad
    minim veniam, quis nostrud exercitation ullamco laboris nisi ut
    aliquip ex ea commodo consequat. Duis aute irure dolor in
    reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla
    pariatur. Excepteur sint occaecat cupidatat non proident, sunt in
    culpa qui officia deserunt mollit anim id est laborum.

    The value of :math:`\omega` is larger than 5.

    """
    )
    actual = getdoc(foo)
    compare(actual, expected)
    validate(foo)


def test_references():
    # noinspection PyUnusedLocal
    @doc(
        summary="A function with simple parameters.",
        parameters=dict(
            bar="This is very bar.",
            baz="This is totally baz.",
        ),
        returns=dict(
            qux="Amazingly qux.",
        ),
        notes="""
            The algorithm is cool and is described in [1]_ and [CIT2002]_.
        """,
        references={
            "1": 'O. McNoleg, "The integration of GIS, remote sensing, expert systems and adaptive co-kriging for environmental habitat modelling of the Highland Haggis using object-oriented, fuzzy-logic and neural-network techniques," Computers & Geosciences, vol. 22, pp. 585-588, 1996.',  # noqa
            "CIT2002": "Book or article reference, URL or whatever.",
        },
    )
    def foo(bar, baz):
        pass

    expected = cleandoc(
        """
    A function with simple parameters.

    Parameters
    ----------
    bar :
        This is very bar.
    baz :
        This is totally baz.

    Returns
    -------
    qux :
        Amazingly qux.

    Notes
    -----
    The algorithm is cool and is described in [1]_ and [CIT2002]_.

    References
    ----------
    .. [1] O. McNoleg, "The integration of GIS, remote sensing, expert systems
        and adaptive co-kriging for environmental habitat modelling of the
        Highland Haggis using object-oriented, fuzzy-logic and neural-
        network techniques," Computers & Geosciences, vol. 22, pp. 585-588,
        1996.
    .. [CIT2002] Book or article reference, URL or whatever.

    """
    )
    actual = getdoc(foo)
    compare(actual, expected)
    validate(foo)


def test_examples():
    # noinspection PyUnusedLocal
    @doc(
        summary="A function with simple parameters.",
        parameters=dict(
            bar="This is very bar.",
            baz="This is totally baz.",
        ),
        returns=dict(
            qux="Amazingly qux.",
        ),
        examples="""
            These are written in doctest format, and should illustrate how to use the function.

            >>> a = [1, 2, 3]
            >>> print([x + 3 for x in a])
            [4, 5, 6]
            >>> print("a\\nb")
            a
            b

            Here are some more examples.

            >>> np.add(1, 2)
            3

            Comment explaining the second example.

            >>> np.add([1, 2], [3, 4])
            array([4, 6])

            Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

            >>> np.add([[1, 2], [3, 4]], [[5, 6], [7, 8]])
            array([[ 6,  8],
                   [10, 12]])

        """,  # noqa
    )
    def foo(bar, baz):
        pass

    expected = cleandoc(
        """
    A function with simple parameters.

    Parameters
    ----------
    bar :
        This is very bar.
    baz :
        This is totally baz.

    Returns
    -------
    qux :
        Amazingly qux.

    Examples
    --------
    These are written in doctest format, and should illustrate how to use
    the function.

    >>> a = [1, 2, 3]
    >>> print([x + 3 for x in a])
    [4, 5, 6]
    >>> print("a\\nb")
    a
    b

    Here are some more examples.

    >>> np.add(1, 2)
    3

    Comment explaining the second example.

    >>> np.add([1, 2], [3, 4])
    array([4, 6])

    Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
    eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad
    minim veniam, quis nostrud exercitation ullamco laboris nisi ut
    aliquip ex ea commodo consequat. Duis aute irure dolor in
    reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla
    pariatur. Excepteur sint occaecat cupidatat non proident, sunt in
    culpa qui officia deserunt mollit anim id est laborum.

    >>> np.add([[1, 2], [3, 4]], [[5, 6], [7, 8]])
    array([[ 6,  8],
           [10, 12]])

    """
    )
    actual = getdoc(foo)
    compare(actual, expected)
    validate(foo)


# noinspection PyUnusedLocal
@doc(
    summary="Compute the arithmetic mean along the specified axis.",
    extended_summary="""
        Returns the average of the array elements.  The average is taken over
        the flattened array by default, otherwise over the specified axis.
        `float64` intermediate and return values are used for integer inputs.
    """,
    parameters=dict(
        a="""
            Array containing numbers whose mean is desired. If `a` is not an
            array, a conversion is attempted.
        """,
        axis="""
            Axis or axes along which the means are computed. The default is to
            compute the mean of the flattened array.

            .. versionadded:: 1.7.0

            If this is a tuple of ints, a mean is performed over multiple axes,
            instead of a single axis or all the axes as before.
        """,
        dtype="""
            Type to use in computing the mean.  For integer inputs, the default
            is `float64`; for floating point inputs, it is the same as the
            input dtype.
        """,
        out="""
            Alternate output array in which to place the result.  The default
            is ``None``; if provided, it must have the same shape as the
            expected output, but the type will be cast if necessary.
            See :ref:`ufuncs-output-type` for more details.
        """,
        keepdims="""
            If this is set to True, the axes which are reduced are left
            in the result as dimensions with size one. With this option,
            the result will broadcast correctly against the input array.

            If the default value is passed, then `keepdims` will not be
            passed through to the `mean` method of sub-classes of
            `ndarray`, however any non-default value will be.  If the
            sub-class' method does not implement `keepdims` any
            exceptions will be raised.
        """,
        where="""
            Elements to include in the mean. See `~numpy.ufunc.reduce` for details.

            .. versionadded:: 1.20.0

        """,
    ),
    returns=dict(
        m="""
            If `out=None`, returns a new array containing the mean values,
            otherwise a reference to the output array is returned.
        """
    ),
    see_also=dict(
        average="Weighted average",
        std=None,
        var=None,
        nanmean=None,
        nanstd=None,
        nanvar=None,
    ),
    notes="""
        The arithmetic mean is the sum of the elements along the axis divided
        by the number of elements.

        Note that for floating-point input, the mean is computed using the
        same precision the input has.  Depending on the input data, this can
        cause the results to be inaccurate, especially for `float32` (see
        example below).  Specifying a higher-precision accumulator using the
        `dtype` keyword can alleviate this issue.

        By default, `float16` results are computed using `float32` intermediates
        for extra precision.
    """,
    examples="""
        >>> a = np.array([[1, 2], [3, 4]])
        >>> np.mean(a)
        2.5
        >>> np.mean(a, axis=0)
        array([2., 3.])
        >>> np.mean(a, axis=1)
        array([1.5, 3.5])

        In single precision, `mean` can be inaccurate:

        >>> a = np.zeros((2, 512 * 512), dtype=np.float32)
        >>> a[0, :] = 1.0
        >>> a[1, :] = 0.1
        >>> np.mean(a)
        0.54999924

        Computing the mean in float64 is more accurate:

        >>> np.mean(a, dtype=np.float64)
        0.55000000074505806 # may vary

        Specifying a where argument:

        >>> a = np.array([[5, 9, 13], [14, 10, 12], [11, 15, 19]])
        >>> np.mean(a)
        12.0
        >>> np.mean(a, where=[[True], [False], [False]])
        9.0
    """,
)
def numpy_mean(
    a: ArrayLike,
    axis: Optional[Union[int, Tuple[int, ...]]] = None,
    dtype: Optional[DTypeLike] = None,
    out: Optional[numpy.ndarray] = None,
    keepdims: Optional[bool] = None,
    *,
    where: Optional[ArrayLike] = None,
) -> numpy.ndarray:
    return numpy.zeros(42)


def test_numpy_mean():
    expected = cleandoc(
        """
    Compute the arithmetic mean along the specified axis.

    Returns the average of the array elements.  The average is taken over
    the flattened array by default, otherwise over the specified axis.
    `float64` intermediate and return values are used for integer inputs.

    Parameters
    ----------
    a : array_like
        Array containing numbers whose mean is desired. If `a` is not an
        array, a conversion is attempted.
    axis : int or tuple of int or None, optional
        Axis or axes along which the means are computed. The default is to
        compute the mean of the flattened array.

        .. versionadded:: 1.7.0

        If this is a tuple of ints, a mean is performed over multiple axes,
        instead of a single axis or all the axes as before.
    dtype : data-type, optional
        Type to use in computing the mean.  For integer inputs, the default is
        `float64`; for floating point inputs, it is the same as the input
        dtype.
    out : ndarray or None, optional
        Alternate output array in which to place the result.  The default is
        ``None``; if provided, it must have the same shape as the expected
        output, but the type will be cast if necessary. See :ref:`ufuncs-
        output-type` for more details.
    keepdims : bool or None, optional
        If this is set to True, the axes which are reduced are left in the
        result as dimensions with size one. With this option, the result will
        broadcast correctly against the input array.

        If the default value is passed, then `keepdims` will not be passed
        through to the `mean` method of sub-classes of `ndarray`, however any
        non-default value will be.  If the sub-class' method does not
        implement `keepdims` any exceptions will be raised.
    where : array_like or None, optional
        Elements to include in the mean. See `~numpy.ufunc.reduce` for
        details.

        .. versionadded:: 1.20.0

    Returns
    -------
    m : ndarray
        If `out=None`, returns a new array containing the mean values,
        otherwise a reference to the output array is returned.

    See Also
    --------
    average : Weighted average.
    std
    var
    nanmean
    nanstd
    nanvar

    Notes
    -----
    The arithmetic mean is the sum of the elements along the axis divided
    by the number of elements.

    Note that for floating-point input, the mean is computed using the
    same precision the input has.  Depending on the input data, this can
    cause the results to be inaccurate, especially for `float32` (see
    example below).  Specifying a higher-precision accumulator using the
    `dtype` keyword can alleviate this issue.

    By default, `float16` results are computed using `float32`
    intermediates for extra precision.

    Examples
    --------
    >>> a = np.array([[1, 2], [3, 4]])
    >>> np.mean(a)
    2.5
    >>> np.mean(a, axis=0)
    array([2., 3.])
    >>> np.mean(a, axis=1)
    array([1.5, 3.5])

    In single precision, `mean` can be inaccurate:

    >>> a = np.zeros((2, 512 * 512), dtype=np.float32)
    >>> a[0, :] = 1.0
    >>> a[1, :] = 0.1
    >>> np.mean(a)
    0.54999924

    Computing the mean in float64 is more accurate:

    >>> np.mean(a, dtype=np.float64)
    0.55000000074505806 # may vary

    Specifying a where argument:

    >>> a = np.array([[5, 9, 13], [14, 10, 12], [11, 15, 19]])
    >>> np.mean(a)
    12.0
    >>> np.mean(a, where=[[True], [False], [False]])
    9.0

    """
    )

    actual = getdoc(numpy_mean)
    compare(actual, expected)
    validate(numpy_mean)


def test_example():
    from numpydoc_decorator.example import greet

    expected = cleandoc(
        """
    Say hello to someone.

    Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod
    tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim
    veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea
    commodo consequat. Duis aute irure dolor in reprehenderit in voluptate
    velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint
    occaecat cupidatat non proident, sunt in culpa qui officia deserunt
    mollit anim id est laborum.

    Parameters
    ----------
    name : str
        The name of the person to greet.
    language : str, optional, default: 'en'
        The language in which to greet as an ISO 639-1 code.

    Returns
    -------
    str
        A pleasant greeting.

    Raises
    ------
    NotImplementedError
        If the requested language has not been implemented yet.
    ValueError
        If the language is not a valid ISO 639-1 code.

    See Also
    --------
    print : You could use this function to print your greeting.

    Notes
    -----
    This function is useful when greeting someone else. If you would like
    something to talk about next, you could try [1]_.

    References
    ----------
    .. [1] O. McNoleg, "The integration of GIS, remote sensing, expert systems
        and adaptive co-kriging for environmental habitat modelling of the
        Highland Haggis using object-oriented, fuzzy-logic and neural-
        network techniques," Computers & Geosciences, vol. 22, pp. 585-588,
        1996.

    Examples
    --------
    Here is how to greet a friend in English:

    >>> print(greet("Ford Prefect"))
    Hello Ford Prefect!

    Here is how to greet someone in another language:

    >>> print(greet("Tricia MacMillan", language="fr"))
    Salut Tricia MacMillan!

    """
    )

    actual = getdoc(greet)
    compare(actual, expected)
    validate(greet)


def test_forward_refs():
    # Here we test whether forward references to classes defined after
    # the decorated function are supported.

    # N.B., some of the forward references cause flake8 to be unhappy,
    # but don't seem to be a problem. Hence some use of noqa below.

    @doc(
        summary="A function with typed parameters and forward references.",
        parameters=dict(
            bar="This is very bar.",
            baz="This is totally baz.",
            qux="Many values.",
            spam="You'll love it.",
            eggs="Good with spam.",
            bacon="Good with eggs.",
            sausage="Good with bacon.",
            lobster="Good with sausage.",
            thermidor="A type of lobster dish.",
            # other parameters not needed, will be picked up from Annotated type
        ),
    )
    def foo(
        bar: int,
        baz: str,
        qux: "Thing",
        spam: Union[str, "Thing"],  # noqa
        eggs: Dict[str, "Thing"],  # noqa
        bacon: Literal["xxx", "yyy", "zzz"],
        sausage: List["Thing"],  # noqa
        lobster: Tuple["Thing", ...],  # noqa
        thermidor: Sequence["Thing"],  # noqa
        norwegian_blue: Annotated["Thing", "This is an ex-parrot."],  # noqa
        lumberjack_song: Optional[
            Annotated["Thing", "I sleep all night and I work all day."]  # noqa
        ],
    ):
        pass

    class Thing:
        pass

    expected = cleandoc(
        """
    A function with typed parameters and forward references.

    Parameters
    ----------
    bar : int
        This is very bar.
    baz : str
        This is totally baz.
    qux : Thing
        Many values.
    spam : str or Thing
        You'll love it.
    eggs : dict[str, Thing]
        Good with spam.
    bacon : {'xxx', 'yyy', 'zzz'}
        Good with eggs.
    sausage : list of Thing
        Good with bacon.
    lobster : tuple of Thing
        Good with sausage.
    thermidor : sequence of Thing
        A type of lobster dish.
    norwegian_blue : Thing
        This is an ex-parrot.
    lumberjack_song : Thing or None
        I sleep all night and I work all day.

    """
    )
    actual = getdoc(foo)
    compare(actual, expected)
    validate(foo)

    # check annotated types are bypassed
    compare(foo.__annotations__["norwegian_blue"], ForwardRef("Thing"))
    compare(foo.__annotations__["lumberjack_song"], Optional["Thing"])


def test_annotated_doc():
    # check we can use https://typing-extensions.readthedocs.io/en/latest/#Doc

    from typing_extensions import Doc

    @doc(
        summary="A function with annotated parameters.",
    )
    def foo(
        bar: Annotated[int, Doc("This is very bar.")],
        baz: Annotated[str, Doc("This is totally baz.")],
        qux: Annotated[Sequence, Doc("Many values.")],
        spam: Annotated[Union[list, str], Doc("You'll love it.")],
        eggs: Annotated[Dict[str, Sequence], Doc("Good with spam.")],
        bacon: Annotated[Literal["xxx", "yyy", "zzz"], Doc("Good with eggs.")],
        sausage: Annotated[List[int], Doc("Good with bacon.")],
        lobster: Annotated[Tuple[float, ...], Doc("Good with sausage.")],
        thermidor: Annotated[Sequence[str], Doc("A type of lobster dish.")],
        norwegian_blue: Annotated[str, Doc("This is an ex-parrot.")],
        lumberjack_song: Optional[
            Annotated[int, Doc("I sleep all night and I work all day.")]
        ],
    ):
        pass

    expected = cleandoc(
        """
    A function with annotated parameters.

    Parameters
    ----------
    bar : int
        This is very bar.
    baz : str
        This is totally baz.
    qux : Sequence
        Many values.
    spam : list or str
        You'll love it.
    eggs : dict[str, Sequence]
        Good with spam.
    bacon : {'xxx', 'yyy', 'zzz'}
        Good with eggs.
    sausage : list of int
        Good with bacon.
    lobster : tuple of float
        Good with sausage.
    thermidor : sequence of str
        A type of lobster dish.
    norwegian_blue : str
        This is an ex-parrot.
    lumberjack_song : int or None
        I sleep all night and I work all day.

    """
    )
    actual = getdoc(foo)
    compare(actual, expected)
    validate(foo)

    # check annotated types are stripped
    expected_annotations = {
        "bar": int,
        "baz": str,
        "qux": Sequence,
        "spam": Union[list, str],
        "eggs": Dict[str, Sequence],
        "bacon": Literal["xxx", "yyy", "zzz"],
        "sausage": List[int],
        "lobster": Tuple[float, ...],
        "thermidor": Sequence[str],
        "norwegian_blue": str,
        "lumberjack_song": Optional[int],
    }
    compare(foo.__annotations__, expected_annotations)


def test_annotated_field():
    # check we can use https://docs.pydantic.dev/latest/api/fields/#pydantic.fields.Field

    from pydantic import Field

    @doc(
        summary="A function with annotated parameters.",
    )
    def foo(
        bar: Annotated[int, Field(gt=1), "This is very bar."],
        baz: Annotated[str, Field(description="This is totally baz.")],
        qux: Annotated[Sequence, Field(description="Many values.")],
        spam: Annotated[Union[list, str], Field(description="You'll love it.")],
        eggs: Annotated[Dict[str, Sequence], Field(description="Good with spam.")],
        bacon: Annotated[
            Literal["xxx", "yyy", "zzz"], Field(description="Good with eggs.")
        ],
        sausage: Annotated[List[int], Field(description="Good with bacon.")],
        lobster: Annotated[Tuple[float, ...], Field(description="Good with sausage.")],
        thermidor: Annotated[
            Sequence[str], Field(description="A type of lobster dish.")
        ],
        norwegian_blue: Annotated[str, Field(description="This is an ex-parrot.")],
        lumberjack_song: Optional[
            Annotated[int, Field(description="I sleep all night and I work all day.")]
        ],
    ):
        pass

    expected = cleandoc(
        """
    A function with annotated parameters.

    Parameters
    ----------
    bar : int
        This is very bar.
    baz : str
        This is totally baz.
    qux : Sequence
        Many values.
    spam : list or str
        You'll love it.
    eggs : dict[str, Sequence]
        Good with spam.
    bacon : {'xxx', 'yyy', 'zzz'}
        Good with eggs.
    sausage : list of int
        Good with bacon.
    lobster : tuple of float
        Good with sausage.
    thermidor : sequence of str
        A type of lobster dish.
    norwegian_blue : str
        This is an ex-parrot.
    lumberjack_song : int or None
        I sleep all night and I work all day.

    """
    )
    actual = getdoc(foo)
    compare(actual, expected)
    validate(foo)

    # check annotated types are stripped
    expected_annotations = {
        "bar": int,
        "baz": str,
        "qux": Sequence,
        "spam": Union[list, str],
        "eggs": Dict[str, Sequence],
        "bacon": Literal["xxx", "yyy", "zzz"],
        "sausage": List[int],
        "lobster": Tuple[float, ...],
        "thermidor": Sequence[str],
        "norwegian_blue": str,
        "lumberjack_song": Optional[int],
    }
    compare(foo.__annotations__, expected_annotations)


def test_dataclass():
    @doc(
        summary="This tests @doc for a dataclass.",
        parameters=dict(
            x="This is a number.",
            name="This is a name.",
        ),
    )
    @dataclass
    class MyDC:
        x: int
        name: str

    expected = cleandoc(
        """
    This tests @doc for a dataclass.

    Parameters
    ----------
    x : int
        This is a number.
    name : str
        This is a name.
    """
    )
    actual = getdoc(MyDC)
    compare(actual, expected)
    validate(MyDC)


def test_simple_enum():
    @doc(
        summary="This tests @doc for an enum.",
        attributes=dict(First="This is the 1st value."),
    )
    class MyEnum(Enum):
        First: str = "1st"
        Second: str = "2nd"

    expected = cleandoc(
        """
    This tests @doc for an enum.

    Attributes
    ----------
    First = "1st"
        This is the 1st value.
    Second = "2nd"
    """
    )
    actual = getdoc(MyEnum)
    compare(actual, expected)


def test_extra_enum_attributes_is_error():
    with pytest.raises(DocumentationError) as err_ctx:

        @doc(
            summary="Attributes to doc for enum which aren't members is bad.",
            attributes=dict(
                First="This is the 1st value.",
                Extra1="This isn't a member.",
                Second="Second good value.",
                Extra2="This also isn't a member,",
            ),
        )
        class MyEnum(Enum):
            First: str = "1st"
            Second: str = "2nd"

    assert (
        str(err_ctx.value)
        == "Attributes to document for MyEnum aren't members of that enum: Extra1, Extra2"
    )


def test_undocumented_enum_members_are_properly_stubbed():
    @doc(summary="This tests @doc for an enum.")
    class MyEnum(Enum):
        First: str = "1st"
        Second: str = "2nd"

    expected = cleandoc(
        """
    This tests @doc for an enum.

    Attributes
    ----------
    First = "1st"
    Second = "2nd"
    """
    )
    actual = getdoc(MyEnum)
    compare(actual, expected)


def test_cannot_pass_parameters_and_arguments_for_enum():
    with pytest.raises(DocumentationError) as err_ctx:

        @doc(
            summary="Attributes to doc for enum which aren't members is bad.",
            attributes=dict(First="This is the first value."),
            parameters=dict(Second="This is the next value."),
        )
        class MyEnum(Enum):
            First: str = "1st"
            Second: str = "2nd"

    assert (
        str(err_ctx.value)
        == "Specify either parameters (documenting non-enum) OR attributes (documenting enum), not both"
    )


def test_parameters_rather_than_attributes_for_enum_is_warning_but_properly_used():
    with pytest.warns(
        DeprecationWarning,
        match="For enum documentation, use attributes rather than parameters.",
    ):

        @doc(
            summary="This tests @doc for an enum.",
            parameters=dict(First="This is the 1st value."),
        )
        class MyEnum(Enum):
            First: str = "1st"

    expected = cleandoc(
        """
    This tests @doc for an enum.

    Attributes
    ----------
    First = "1st"
        This is the 1st value.
    """
    )
    actual = getdoc(MyEnum)
    compare(actual, expected)
