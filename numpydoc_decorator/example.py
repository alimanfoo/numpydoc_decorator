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
    returns=dict(
        greeting="A pleasant greeting.",
    ),
    raises=dict(
        NotImplementedError="If the requested language has not been implemented yet.",
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
    if language == "en":
        return f"Hello {name}!"
    elif language == "fr":
        return f"Salut {name}!"
    else:
        raise NotImplementedError(f"language {language} not implemented")
