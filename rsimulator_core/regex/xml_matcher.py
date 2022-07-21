from re import Match as ReMatch
from re import fullmatch, sub

from lxml import etree as et
from lxml.etree import Element, XMLSyntaxError
from rsimulator_core.data import Error
from rsimulator_core.regex.data import Groups


def __error(
    parents: tuple[Element, ...],
    this_element: Element,
    that_element: Element,
    message: str,
) -> Error:
    path = tuple(e.tag for e in parents)
    this = (
        this_element
        if isinstance(this_element, str)
        else et.tostring(this_element).decode("utf-8")
    )
    that = (
        that_element
        if isinstance(that_element, str)
        else et.tostring(that_element).decode("utf-8")
    )
    return Error(path, this, that, message)


def __remove_prolog(xml_str: str) -> str:
    return sub(
        "^<\\?.+\\?>", "", xml_str.strip()
    ).strip()  # '<?xml version="1.0" encoding="UTF-8"?>'


def __match(this_str: str, that_str: str) -> ReMatch[str]:
    return fullmatch(f"(?ms){this_str}", that_str)


def __match_tag(
    this_element: Element, that_element: Element, parents: tuple[Element, ...]
) -> Error | Groups:
    if this_element.tag == that_element.tag:
        return Groups()
    return __error(
        parents,
        this_element,
        that_element,
        f'Names not matching: "{this_element.tag}" != "{that_element.tag}"',
    )


def __match_attr(
    this_element: Element, that_element: Element, parents: tuple[Element, ...]
) -> Error | Groups:
    if this_element.attrib == that_element.attrib:
        return Groups()
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
    return Groups(groups=groups)


def __match_text(
    this_element: Element, that_element: Element, parents: tuple[Element, ...]
) -> Error | Groups:
    this_text, that_text = (
        e.text.strip() if e.text else "" for e in (this_element, that_element)
    )
    if m := __match(this_text, that_text):
        return Groups(groups=tuple(m.groups()))
    return __error(
        parents,
        this_element,
        that_element,
        f'Text not matching: "{this_text}" != "{that_text}"',
    )


def __match_children(
    this_element: Element, that_element: Element, parents: tuple[Element, ...]
) -> Error | Groups:
    if len(this_element) != len(that_element):
        return __error(
            parents, this_element, that_element, "Different number of children"
        )
    groups = tuple()
    for this_child, that_child in zip(
        this_element, that_element
    ):  # children must be in same order
        result = __match_elements(this_child, that_child, parents + (this_element,))
        if isinstance(result, Error):
            return result
        groups += tuple(result.groups)
    return Groups(groups=groups)


def __canonicalize(this_element: Element, that_element: Element) -> tuple[str, str]:
    this_canonicalized, that_canonicalized = (
        et.canonicalize(e, strip_text=True, rewrite_prefixes=True)
        for e in (this_element, that_element)
    )
    return this_canonicalized, that_canonicalized


def __match_elements(
    this_element: Element,
    that_element: Element,
    parents: tuple[Element, ...] = (),
) -> Error | Groups:
    # Return if as canonicalized strings are equal or match as regexp
    this_canonicalized, that_canonicalized = __canonicalize(this_element, that_element)
    if this_canonicalized == that_canonicalized:
        return Groups()
    if m := __match(this_canonicalized, that_canonicalized):
        return Groups(groups=tuple(m.groups()))
    # Match this_element and that_element. Return first Error if encountered, else captured groups
    groups = tuple()
    for f in __match_tag, __match_attr, __match_text, __match_children:
        result = f(this_element, that_element, parents)
        if isinstance(result, Error):
            return result
        groups += result.groups

    return Groups(groups=groups)


def match(this: str, that: str) -> Error | Groups:
    """
    Matches this and that.
    The "this" can contain regular expressions.
    Both "this" and "that" must be valid xml, if they not as a whole matches with
    re.fullmatch(f"(?ms){r}", s).
    Returns an Error or a Groups object.
    """
    if not (isinstance(this, str) and isinstance(that, str)):
        # Return error if this and that are not strings
        return __error(
            (),
            str(this),
            str(that),
            f'Values not strings: "{type(this)}" != "{type(that)}"',
        )

    # Return if this and that are equal or match as regexp
    if this == that:
        return Groups()
    if m := __match(this, that):
        return Groups(groups=tuple(m.groups()))

    # Parse to Elements
    elements = []
    for name, xml in ("this", this), ("that", that):
        try:
            elements.append(
                et.fromstring(__remove_prolog(xml)) if isinstance(xml, str) else xml
            )
        except XMLSyntaxError as e:
            return __error((), this, that, f'Cannot parse "{name}": "{xml}", {e}')
    this_element, that_element = elements

    # Match Elements
    return __match_elements(this_element, that_element)
