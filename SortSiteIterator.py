from SortSiteIteratorAppShell import SortSiteIteratorAppShell
from PyQt5.QtWidgets import QApplication
import sys

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SortSiteIteratorAppShell()
    sys.exit(app.exec_())
