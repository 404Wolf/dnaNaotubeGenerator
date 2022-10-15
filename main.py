import logging
from time import time

# main script logger
logger = logging.getLogger("main")

# mute pyqt logs
logging.getLogger("PyQt6").setLevel(logging.INFO)

# log boot statement
logger.debug(f"Booting @ {time()}")


def main():
    # set log level
    logging.basicConfig(
        level=logging.DEBUG,
    )
    import config  # for initialization
    import storage
    import sys

    if sys.platform.startswith("win"):
        # to get icon to work properly on Windows this code must be run
        # consult the below stackoverflow link for information on why
        # https://stackoverflow.com/questions/1551605/how-to-set-applications-taskbar-icon-in-windows-7/1552105#1552105
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(__name__)

    # show the constructor window
    storage.windows.constructor.show()
    storage.windows.constructor.resizeEvent(None)  # trigger initial resize event
    logger.debug("Set up main window")

    # begin app event loop
    logger.debug("Beginning event loop...")
    sys.exit(storage.application.exec())


if __name__ == "__main__":
    main()
