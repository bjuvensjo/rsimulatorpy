import re
from re import Match
from typing import Optional

from lxml import etree as et
from lxml.etree import XMLSyntaxError, Element

from rsimulator_core.data import Result, Error


def __error(
    parents: Optional[tuple[str, ...]],
    this_element: Optional[Element],
    that_element: Optional[Element],
    message: str,
) -> Result:
    return Result(
        error=Error(
            parents,
            None if this_element is None else this_element.tag,
            None if that_element is None else that_element.tag,
            message,
        )
    )


def __remove_prolog(xml_str: str) -> str:
    return re.sub(
        "^<\\?.+\\?>", "", xml_str.strip()
    ).strip()  # '<?xml version="1.0" encoding="UTF-8"?>'


def __match(this_str: str, that_str: str) -> Match[str]:
    return re.fullmatch(f"(?ms){this_str}", that_str)


def __match_tag(
    this_element: Element, that_element: Element, parents: tuple[str, ...]
) -> Result:
    return (
        Result()
        if this_element.tag == that_element.tag
        else __error(parents, this_element, that_element, "Names not matching")
    )


def __match_attr(
    this_element: Element, that_element: Element, parents: tuple[str, ...]
) -> Result:
    if this_element.attrib == that_element.attrib:
        return Result()
    if len(this_element.attrib) != len(that_element.attrib):
        return __error(
            parents, this_element, that_element, "Different number of attributes"
        )
    groups = tuple()
    for this_key, this_value in this_element.attrib.items():
        # Don't use zip since attributes in different order should match
        that_value = that_element.attrib.get(this_key, "")
        m = __match(this_value, that_value)
        if not m:
            return __error(
                parents,
                this_element,
                that_element,
                f'Attribute values not matching for {this_key}: "{this_value}" != "{that_value}"',
            )
        groups += m.groups()
    return Result(groups=groups)


def __match_text(
    this_element: Element, that_element: Element, parents: tuple[str, ...]
) -> Result:
    this_text, that_text = (
        e.text.strip() if e.text else "" for e in (this_element, that_element)
    )
    m = __match(this_text, that_text)
    if m:
        return Result(groups=tuple(m.groups()))
    return __error(
        parents,
        this_element,
        that_element,
        f'Text not matching: "{this_text}" != "{that_text}"',
    )


def __match_children(
    this_element: Element, that_element: Element, parents: tuple[str, ...]
) -> Result:
    if len(this_element) != len(that_element):
        return __error(
            parents, this_element, that_element, "Different number of children"
        )
    groups = tuple()
    for this_child, that_child in zip(
        this_element, that_element
    ):  # children must be in same order
        result = __match_elements(this_child, that_child, parents + (this_element.tag,))
        if result.has_error():
            return result
        groups += tuple(result.groups)
    return Result(groups=groups)


def __canonicalize(this_element: Element, that_element: Element) -> tuple[str, str]:
    this_canonicalized, that_canonicalized = (
        et.canonicalize(e, strip_text=True, rewrite_prefixes=True)
        for e in (this_element, that_element)
    )
    return this_canonicalized, that_canonicalized


def __match_elements(
    this_element: Element,
    that_element: Element,
    parents=(),
) -> Result:
    # Return if as canonicalized strings and are equal or match as regexp
    this_canonicalized, that_canonicalized = __canonicalize(this_element, that_element)
    if this_canonicalized == that_canonicalized:
        return Result()
    m = __match(this_canonicalized, that_canonicalized)
    if m:
        return Result(groups=tuple(m.groups()))
    # Match this_element and that_element. Return first Error if encountered, else captured groups
    groups = tuple()
    for f in __match_tag, __match_attr, __match_text, __match_children:
        result = f(this_element, that_element, parents)
        if result.has_error():
            return result
        groups += result.groups

    return Result(groups=groups)


def match(this: str, that: str) -> Result:
    """
    Matches this and that.
    The "this" can contain regular expressions.
    Both "this" and "that" must be valid xml, if they not as a whole matches with
    re.fullmatch(f"(?ms){r}", s).
    Returns a Result object with possible groups and/or errors
    """
    if not (isinstance(this, str) and isinstance(that, str)):
        # Return error if this and that are not strings
        return __error(
            (),
            None,
            None,
            f'Values not strings: "{type(this)}" != "{type(that)}"',
        )

    # Return if this and that are equal or match as regexp
    if this == that:
        return Result()
    m = __match(this, that)
    if m:
        return Result(groups=tuple(m.groups()))

    # Parse to Elements
    elements = []
    for name, xml in ("this", this), ("that", that):
        try:
            elements.append(
                et.fromstring(__remove_prolog(xml)) if isinstance(xml, str) else xml
            )
        except XMLSyntaxError as e:
            return __error(None, None, None, f'Cannot parse "{name}": "{xml}", {e}')
    this_element, that_element = elements

    # Match Elements
    return __match_elements(this_element, that_element)
