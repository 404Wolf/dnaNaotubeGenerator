import logging

from PyQt6.QtWidgets import QHeaderView

from structures.profiles import NucleicAcidProfile
from ui.config.tabs.domains.tables.base import DomainsBaseTable

logger = logging.getLogger(__name__)


class DomainsAnglesTable(DomainsBaseTable):
    """Nucleic Acid Config Tab."""

    def __init__(self, parent, nucleic_acid_profile: NucleicAcidProfile) -> None:
        super().__init__(
            parent,
            ["L-Joint", "R-Joint", "s", "m", "θi"],
        )
        # Store the nucleic acid nucleic_acid_profile
        self.nucleic_acid_profile = nucleic_acid_profile

    def _prettify(self):
        super()._prettify()

        # Use ResizeToContents for the header size policy
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
