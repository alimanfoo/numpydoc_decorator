# numpydoc_decorator

This package allows you to build [numpy-style
docstrings](https://numpydoc.readthedocs.io/en/latest/format.html#sections)
programmatically and apply them using a decorator. This can be useful
because:

-   Parts of your documentation, such as parameter descriptions, can be
    shared between functions, avoiding the need to repeat yourself.

-   Type information for parameters and return values is automatically
    picked up from type annotations and added to the docstring, avoiding
    the need to maintain type information in two places.

## Installation

`pip install numpydoc_decorator`

## Usage

### Documentation a function

Here is an example of documenting a function:

```python
from numpydoc_decorator import doc


@doc(
    summary="Say hello to someone.",
    extended_summary="""
        Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
        eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad
        minim veniam, quis nostrud exercitation ullamco laboris nisi ut
        aliquip ex ea commodo consequat. Duis aute irure dolor in
        reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla
        pariatur. Excepteur sint occaecat cupidatat non proident, sunt in
        culpa qui officia deserunt mollit anim id est laborum.
    """,
    parameters=dict(
        name="The name of the person to greet.",
        language="The language in which to greet as an ISO 639-1 code.",
    ),
    returns="A pleasant greeting.",
    raises=dict(
        NotImplementedError="If the requested language has not been implemented yet.",
        ValueError="If the language is not a valid ISO 639-1 code."
    ),
    see_also=dict(
        print="You could use this function to print your greeting.",
    ),
    notes="""
        This function is useful when greeting someone else. If you would
        like something to talk about next, you could try [1]_.
    """,
    references={
        "1": """
            O. McNoleg, "The integration of GIS, remote sensing, expert systems
            and adaptive co-kriging for environmental habitat modelling of the
            Highland Haggis using object-oriented, fuzzy-logic and neural-
            network techniques," Computers & Geosciences, vol. 22, pp. 585-588,
            1996.
        """,
    },
    examples="""
        Here is how to greet a friend in English:

        >>> print(greet("Ford Prefect"))
        Hello Ford Prefect!

        Here is how to greet someone in another language:

        >>> print(greet("Tricia MacMillan", language="fr"))
        Salut Tricia MacMillan!

    """,
)
def greet(
    name: str,
    language: str = "en",
) -> str:
    if len(language) != 2:
        raise ValueError("language must be an ISO 639-1 code")
    if language == "en":
        return f"Hello {name}!"
    elif language == "fr":
        return f"Salut {name}!"
    else:
        raise NotImplementedError(f"language {language} not implemented")
```

Here is the docstring that will be created and attached to the
decorated function:

```
>>> print(greet.__doc__)

Say hello to someone.

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad
minim veniam, quis nostrud exercitation ullamco laboris nisi ut
aliquip ex ea commodo consequat. Duis aute irure dolor in
reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla
pariatur. Excepteur sint occaecat cupidatat non proident, sunt in
culpa qui officia deserunt mollit anim id est laborum.

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
    Highland Haggis using object-oriented, fuzzy-logic and neural- network
    techniques," Computers & Geosciences, vol. 22, pp. 585-588, 1996.

Examples
--------
Here is how to greet a friend in English:

>>> print(greet("Ford Prefect"))
Hello Ford Prefect!

Here is how to greet someone in another language:

>>> print(greet("Tricia MacMillan", language="fr"))
Salut Tricia MacMillan!

```

### Shared parameters

If you have parameters which are common to multiple functions, here
is an approach you can take:

```python
from numpydoc_decorator import doc
from typing_extensions import Annotated


class params:
    name = Annotated[str, "The name of a person."]
    language = Annotated[str, "An ISO 639-1 language code."]


@doc(
    summary="Say hello to someone you know.",
    returns="A personal greeting.",
)
def say_hello(
    name: params.name,
    language: params.language,
) -> str:
    pass


@doc(
    summary="Say goodbye to someone you know.",
    returns="A personal parting.",
)
def say_goodbye(
    name: params.name,
    language: params.language,
) -> str:
    pass
```

Here are the generated docstrings:

```
>>> print(say_hello.__doc__)

Say hello to someone you know.

Parameters
----------
name : str
    The name of a person.
language : str
    An ISO 639-1 language code.

Returns
-------
str
    A personal greeting.
```

```
>>> print(say_goodbye.__doc__)

Say goodbye to someone you know.

Parameters
----------
name : str
    The name of a person.
language : str
    An ISO 639-1 language code.

Returns
-------
str
    A personal parting.
```

## Notes

There are probably lots of edge cases that this package has not
covered yet. If you find something doesn't work as expected, or
deviates from the [numpydoc style guide](https://numpydoc.readthedocs.io/en/latest/format.html)
in an unreasonable way, please feel free to submit a pull request.

Note that this package does deviate from the numpydoc style guide
under some circumstances. For example, if a function does not have
any type annotations, then there will be no type information in the
docstring. The rationale for this is that all type information, if
provided, should be provided through type annotations. However, some
functions may choose not to annotate types for some or all parameters,
but we still want to document them as best we can.
