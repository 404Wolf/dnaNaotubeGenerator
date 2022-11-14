import atexit
import logging
from contextlib import suppress
from copy import copy
from math import ceil, dist
from typing import List

import pyqtgraph as pg
from PyQt6 import uic
from PyQt6.QtGui import (
    QPen,
)
from PyQt6.QtWidgets import QDialog

import refs
import settings
from constants.directions import *
from constants.modes import *
from structures.points import NEMid
from structures.points.nick import Nick
from structures.strands.strand import Strand

logger = logging.getLogger(__name__)


class Plotter(pg.PlotWidget):
    """The refs plot widget for the Plotter"""

    def __init__(self):
        """Initialize plotter instance."""
        super().__init__()
        self.plot_items = []
        self._width = lambda: refs.strands.current.size[0]
        self._height = lambda: refs.strands.current.size[1]

        self.disableAutoRange()
        self._plot()
        self.autoRange()
        self.setXRange(0, self._width())
        self._prettify()

        # set up styling
        self.setWindowTitle("Side View of DNA")  # set the window's title

    def clear(self):
        for plot_item in self.plot_items:
            self.removeItem(plot_item)

    def refresh(self):
        self.clear()
        self._plot()
        logger.info("Refreshed side view.")

    def point_clicked(self, event, points):
        """Called when a point on a strand is clicked."""
        point = points[0]
        located = []
        for strand in refs.strands.current.strands:
            for item in strand.items:
                if dist(point.pos(), item.position()) < settings.junction_threshold:
                    located.append(item)
        for item in located:
            with suppress(AttributeError):
                if item.pseudo:
                    located.remove(item)

        refresh = refs.constructor.side_view.refresh

        if refs.mode.current == INFORMER:
            dialogs = []

            for item in located:
                item.highlighted = True

                if isinstance(item, NEMid):
                    if item.junctable:
                        logger.debug(
                            f"NEMid's juncmate is in strand#{refs.strands.current.strands.index(item.juncmate.strand)}"
                        )
                        logger.debug(
                            f"NEMid is in strand#{refs.strands.current.strands.index(item.strand)}"
                        )
                    dialog = QDialog(refs.constructor)
                    dialog.setWindowTitle("NEMid Information")
                    uic.loadUi("ui/panels/side_view/informers/NEMid.ui", dialog)
                    dialog.x_coordinate.setText(f"{item.x_coord:.4f} nanometers")
                    dialog.z_coordinate.setText(f"{item.z_coord:.4f} nanometers")
                    dialog.angle.setText(f"{item.angle:.4f}°")

                    strand_index = refs.strands.current.strands.index(item.strand)
                    if item.strand.closed:
                        openness = "closed"
                    else:  # not item.strand.closed
                        openness = "open"
                    dialog.strand.setText(
                        f"item #{item.index} in {openness} strand #{strand_index}"
                    )

                    dialog.original_domain.setText(
                        f"domain #{item.domain.index + 1} of {refs.domains.current.count} domains"
                    )

                    if item.direction == UP:
                        dialog.up.setChecked(True)
                    elif item.direction == DOWN:
                        dialog.down.setChecked(True)

                    dialog.junctable.setChecked(item.junctable)
                    dialog.junction.setChecked(item.junction)

                    dialogs.append(dialog)

            def dialog_complete():
                for dialog in dialogs:
                    dialog.close()
                for item in located:
                    item.highlighted = False
                refresh()

            for dialog in dialogs:
                dialog.finished.connect(dialog_complete)
                dialog.show()
            atexit.register(dialog_complete)

            refresh()

        if refs.mode.current == JUNCTER:
            if len(located) == 2:
                if all([isinstance(item, NEMid) for item in located]):
                    refs.strands.current.junct(located[0], located[1])
                    refresh()
        elif refs.mode.current == NICKER:
            for item in located:
                if refs.mode.current == NICKER:
                    if isinstance(item, NEMid):
                        Nick.to_nick(item)
                    elif isinstance(item, Nick):
                        strand = item.prior.strand
                        strand.items[strand.items.index(item)] = item.prior
            refresh()

    def _prettify(self):
        # create pen for custom grid
        grid_pen: QPen = pg.mkPen(color=settings.colors["grid_lines"], width=1.4)

        # domain index grid
        for i in range(ceil(refs.strands.current.size[0]) + 1):
            self.addLine(x=i, pen=grid_pen)

        # for i in <number of helical twists of the tallest domain>...
        for i in range(0, ceil(self._width() / refs.nucleic_acid.current.H) + 1):
            self.addLine(y=(i * refs.nucleic_acid.current.H), pen=grid_pen)

        # add axis labels
        self.setLabel("bottom", text="Helical Domain")
        self.setLabel("left", text="Helical Twists", units="nanometers")

    def _plot(self):
        bars = []
        plotted_strands = []

        for _strand in refs.strands.current.strands:
            strand = copy(_strand)
            assert isinstance(strand, Strand)

            if strand.closed:
                strand.items.append(strand.items[0])
                strand.items[-1].pseudo = True

            symbols: List[str] = []
            symbol_sizes: List[str] = []
            x_coords: List[float] = []
            z_coords: List[float] = []

            NEMid_brush = pg.mkBrush(color=strand.color)
            nick_brush = pg.mkBrush(color=(settings.colors["nicks"]))
            brushes = []

            if not strand.interdomain:
                pen = pg.mkPen(color=strand.color, width=2, pxMode=False)
            else:
                pen = pg.mkPen(color=strand.color, width=10, pxMode=False)

            for index, item in enumerate(strand.items):
                # if the item is junctable and its juncmate is in this strand
                # it may be plot as if it were two different strands
                # so we add a white line to fix this issue
                if (
                    isinstance(item, NEMid)
                    and item.junctable
                    and item.juncmate is not None
                    and item.juncmate.strand is _strand
                    and strand.interdomain
                ):
                    with suppress(IndexError):
                        # if we've reached a junctable area and the strand continues to change its z coord
                        # create a horizontal line so that it doesn't look like it's branched into a new strand
                        if (
                            abs(item.z_coord - strand.items[index + 1].z_coord) > 0.2
                            and abs(item.z_coord - strand.items[index + 2].z_coord)
                            > 0.2
                        ):
                            # create horizontal line
                            bar_x_coords = item.x_coord - 0.4, item.x_coord + 0.4
                            bar_z_coords = [item.z_coord] * 2
                            # if near_boundaries:
                            #     # create horizontal line
                            #     bar_x_coords = item.x_coord - 0.4, item.x_coord + 0.4
                            #     bar_z_coords = [item.z_coord] * 2
                            #
                            # else:
                            #     # create vertical line
                            #     bar_x_coords = [item.x_coord] * 2
                            #     bar_z_coords = item.z_coord - 0.4, item.z_coord + 0.4

                        bar = pg.PlotDataItem(
                            bar_x_coords,
                            bar_z_coords,
                            pen=pg.mkPen(
                                color=(255, 255, 255), width=8, px_mode=False
                            ),
                        )
                        bars.append(bar)

                x_coords.append(item.x_coord)
                z_coords.append(item.z_coord)

                if isinstance(item, NEMid):
                    if item.direction == UP:
                        symbols.append("t1")  # up arrow
                    elif item.direction == DOWN:
                        symbols.append("t")  # down arrow
                    else:
                        raise ValueError("item.direction is not UP or DOWN.", item)

                    if item.highlighted:
                        symbol_sizes.append(18)
                        brushes.append(pg.mkBrush(color=settings.colors["highlighted"]))
                    else:
                        symbol_sizes.append(6)
                        brushes.append(NEMid_brush)

                elif isinstance(item, Nick):
                    symbol_sizes.append(15)
                    symbols.append("o")
                    brushes.append(nick_brush)

            # create a PlotDataItem of the strand to be plotted later
            outline_only = pg.PlotDataItem(
                x_coords,
                z_coords,
                symbol=None,  # type of symbol (in this case up/down arrow)
                symbolSize=None,  # size of arrows in px
                pxMode=False,  # means that symbol size is in px and non-dynamic
                symbolBrush=None,  # set color of points to current color
                pen=pen,
            )
            points_only = pg.PlotDataItem(
                x_coords,
                z_coords,
                symbol=symbols,  # type of symbol (in this case up/down arrow)
                symbolSize=symbol_sizes,  # size of arrows in px
                pxMode=True,  # means that symbol size is in px and non-dynamic
                symbolBrush=brushes,  # set color of points to current color
                pen=None,
            )

            plotted_strands.append(
                (
                    outline_only,
                    points_only,
                )
            )

        for outline_only, points_only in plotted_strands:
            self.addItem(outline_only)
            self.plot_items.append(outline_only)

        for bar in bars:
            self.addItem(bar)
            self.plot_items.append(bar)

        for outline_only, points_only in plotted_strands:
            self.addItem(points_only)
            points_only.sigPointsClicked.connect(self.point_clicked)
            self.plot_items.append(points_only)

        self._prettify()
