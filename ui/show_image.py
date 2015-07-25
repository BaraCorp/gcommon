#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fad
from __future__ import (unicode_literals, absolute_import, division, print_function)

from PyQt4.QtCore import QUrl, SIGNAL
from PyQt4.QtGui import QDialog, QVBoxLayout, QPixmap

from PyQt4 import QtCore, QtGui

from Common.ui.common import FWidget
from configuration import Config


class ShowImageViewWidget(QtGui.QDialog, FWidget):

    def __init__(self, prod="", parent=0, *args, **kwargs):
        super(ShowImageViewWidget, self).__init__(parent=parent, *args, **kwargs)

        self.setWindowTitle("Image: %s" % prod.name.title())

        self.prod = prod
        vbox = QtGui.QVBoxLayout()
        pixmap = QtGui.QPixmap(self.prod.image_link)
        self.imageLabel = QtGui.QLabel(self)
        self.imageLabel.setBackgroundRole(QtGui.QPalette.Base)
        self.imageLabel.setSizePolicy(QtGui.QSizePolicy.Ignored,
                                      QtGui.QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(True)
        self.imageLabel.setPixmap(pixmap)
        self.imageLabel.adjustSize()
        self.setMinimumSize(900, 600)
        myScrollArea = QtGui.QScrollArea()
        myScrollArea.setWidgetResizable(True)
        # myScrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        # myScrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        myScrollArea.setWidget(self.imageLabel)
        vbox.addWidget(myScrollArea)

        self.setLayout(vbox)
