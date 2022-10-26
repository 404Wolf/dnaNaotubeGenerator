import logging

from PyQt6.QtWidgets import QDockWidget

from constructor.panels.config.panel import Panel

logger = logging.getLogger(__name__)


class Dockable(QDockWidget):
    def __init__(self):
        super().__init__()

        # set titles/descriptions
        self.setObjectName("Config Panel")
        self.setStatusTip("Config panel")
        self.setWindowTitle("Config")

        # store the actual link to the widget in self.config
        self.panel = Panel(self)
        self.setWidget(self.panel)
