from typing import List, Iterable

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QTextEdit

from constants.bases import DNA


class DisplayArea(QTextEdit):
    """
    A sequence display area.

    Attributes:
        bases: The bases in the editor area.
    """

    space = "<span style='background-color: rgb(210, 210, 210)'>&nbsp;</span>"
    nonspace = "<span style='background-color: rgb(240, 240, 240)'>{char}</span>"
    highlighted = "<span style='background-color: rgb(245, 245, 0)'>{char}</span>"

    def __init__(self, parent, bases: Iterable[str | None]):
        """
        Initialize the display area.

        Args:
            parent: The parent widget.
            bases: The bases for the editor area.
        """
        super().__init__(parent)
        self._bases = bases

        font = QFont("Courier New", 11)
        self.setFont(font)
        self.setReadOnly(True)
        self.setStyleSheet(
            """QPlainTextEdit::disabled{
            background-color: rgb(255, 255, 255); 
            color: rgb(0, 0, 0)
            }"""
        )
        self.setFixedHeight(285)

        self.refresh()

    @property
    def bases(self):
        """Obtain the current bases."""
        return self._bases

    @bases.setter
    def bases(self, bases: List[str | None]):
        """Change the displayed and stored bases."""
        self._bases = bases
        self.refresh()

    def refresh(self):
        html = ""
        for base in self.bases:
            if base in DNA:
                html += self.nonspace.format(char=base)
            elif base is None:
                html += self.space
            else:
                raise ValueError(f"Base {base} is not a valid base.")
        self.setHtml(html)

    def highlight(self, index):
        """
        Highlight a specific index's character.

        Args:
            index: Character index to highlight.
        """
        html = ""
        for index_, base in enumerate(self.bases):
            if base is None:
                html += self.space
            elif index_ == index:
                html += self.highlighted.format(char=base)
            else:
                html += self.nonspace.format(char=base)
        self.setHtml(html)
