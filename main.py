import dna_nanotube_tools
from PyQt6.QtWidgets import QApplication
import sys

interior_angle_multiples = [4]
switch_angle_multiples = [0]
interior_angle_multiples = [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9]
switch_angle_multiples = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]


def test_top_view():
    top_view = dna_nanotube_tools.plot.top_view(
        interior_angle_multiples, switch_angle_multiples, 2.3
    )

    # print out the cords
    cords = top_view.cords()
    cords = [(round(u, 2), round(v, 2)) for u, v in cords]
    print(cords)

    # display the widget as a window
    app = QApplication(sys.argv)
    ui = top_view.ui()
    ui.show()
    app.exec()


def test_side_view():
    base_angle = 2 * (360 / 21)
    side_view = dna_nanotube_tools.plot.side_view(
        interior_angle_multiples, 3.38, base_angle, 12.6, 2.3
    )
    xs = side_view.xs(10)[0]
    zs = side_view.zs(10)[0]
    xs = xs[0]
    zs = zs[0]

    # display the widget as a window
    app = QApplication(sys.argv)
    import pyqtgraph as pg

    ui = pg.plot(
        xs,
        zs,
        title="Side View of DNA",
        symbol="o",
        symbolSize=4,
        pxMode=True,
    )
    ui.setAspectLocked(lock=True, ratio=1)
    ui.showGrid(x=True, y=True)
    ui.show()
    app.exec()


test_top_view()
