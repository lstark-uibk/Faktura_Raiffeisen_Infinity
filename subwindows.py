import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
from matplotlib.pyplot import title
from bs4 import BeautifulSoup

from nc_py_api import Nextcloud
import imaplib
import email
from email.header import decode_header
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget, QTextEdit, QFormLayout, QScrollArea
import sys


class Subwindow(QMainWindow):
    def __init__(self, Windowname,  Menubardata = [],*args,**kwargs):
        # menubar has to be [[Text,Shortcut,function]]
        super(Subwindow, self).__init__(*args, **kwargs)
        print("Initializing Subwindow")
        self.windowname = Windowname
        self.menubardata = Menubardata
        self.setWindowTitle(self.windowname)

        self.init_Ui_overview()

    def init_Ui_overview(self):
        self.centralwidget = QtWidgets.QWidget(self)
        # main layout setup
        self.overallverticallayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.verticalLayout0 = QtWidgets.QVBoxLayout()  # layout on the left with the masslist, and other stuff
        self.verticalLayout1 = QtWidgets.QVBoxLayout()  # laout on the right with the graph
        if self.menubardata:
            menubar = QtWidgets.QMenuBar()
            self.actionFile = menubar.addMenu("Datei")
            # the po.importanythingact triggers init_UI_file_loaded() and init_plots()
            for menuline in self.menubardata:
                action = QtWidgets.QAction(menuline[0], self)
                action.triggered.connect(menuline[2])
                if menuline[1]:
                    action.setShortcut(menuline[1])
                self.actionFile.addAction(action)

            self.actionFile.addSeparator()
            quit = QtWidgets.QAction("Schließen", self)
            quit.setShortcut("Alt+F4")
            quit.triggered.connect(lambda: sys.exit(0))
            self.actionFile.addAction(quit)

            self.overallverticallayout.addWidget(menubar)
        self.overallverticallayout.addLayout(self.horizontalLayout)
        self.setCentralWidget(self.centralwidget)

