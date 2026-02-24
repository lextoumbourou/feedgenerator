"""
Utilities for XML generation/parsing.
"""

import re
from xml.sax.saxutils import XMLGenerator


class UnserializableContentError(ValueError):
    pass


class SimplerXMLGenerator(XMLGenerator):
    def addQuickElement(self, name, contents=None, attrs=None):
        "Convenience method for adding an element with no children"
        if attrs is None:
            attrs = {}
        self.startElement(name, attrs)
        if contents is not None:
            self.characters(contents)
        self.endElement(name)

    def characters(self, content):
        if content and re.search(r"[\x00-\x08\x0B-\x0C\x0E-\x1F]", content):
            # Fail loudly when content has control chars (unsupported in XML 1.0)
            # See https://www.w3.org/International/questions/qa-controls
            bad_chars = re.findall(r"[\x00-\x08\x0B-\x0C\x0E-\x1F]", content)
            bad_chars_hex = [hex(ord(c)) for c in bad_chars[:5]]
            preview = content[:200] + "..." if len(content) > 200 else content
            raise UnserializableContentError(
                f"Control characters {bad_chars_hex} are not supported in XML 1.0. "
                f"Content preview: {preview!r}"
            )
        XMLGenerator.characters(self, content)

    def startElement(self, name, attrs):
        # Sort attrs for a deterministic output.
        sorted_attrs = dict(sorted(attrs.items())) if attrs else attrs
        super().startElement(name, sorted_attrs)
