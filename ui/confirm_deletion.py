#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fad
from __future__ import (unicode_literals, absolute_import, division, print_function)

from PyQt4.QtGui import QVBoxLayout, QDialog, QGridLayout, QHBoxLayout
from PyQt4.QtCore import Qt


from Common.ui.common import (FWidget, FPageTitle, Button, FLabel)
from Common.ui.util import raise_success


class ConfirmDeletionDiag(QDialog, FWidget):

    def __init__(self, obj_delete, msg, table_p, parent, *args, **kwargs):
        QDialog.__init__(self, parent, *args, **kwargs)

        self.obj_delete = obj_delete
        self.msg = msg
        self.table_p = table_p

        self.setWindowTitle(u"Confirmation de le suppression")
        self.title = FPageTitle(u"Voulez vous vraiment le supprimer?")

        self.title.setAlignment(Qt.AlignHCenter)
        title_hbox = QHBoxLayout()
        title_hbox.addWidget(self.title)
        report_hbox = QGridLayout()

        report_hbox.addWidget(FLabel(self.msg), 0, 0)
        #delete and cancel hbox
        Button_hbox = QHBoxLayout()

        #Delete Button widget.
        delete_but = Button(u"Supprimer")
        Button_hbox.addWidget(delete_but)
        delete_but.clicked.connect(self.delete)
        #Cancel Button widget.
        cancel_but = Button(u"Annuler")
        Button_hbox.addWidget(cancel_but)
        cancel_but.clicked.connect(self.cancel)

        #Create the QVBoxLayout contenaire.
        vbox = QVBoxLayout()
        vbox.addLayout(title_hbox)
        vbox.addLayout(report_hbox)
        vbox.addLayout(Button_hbox)
        self.setLayout(vbox)

    def cancel(self):
        self.close()

    def delete(self):
        self.obj_delete.delete_instance()
        self.cancel()
        self.table_p.refresh_()
        raise_success(u"Confirmation", u"<b>Suppression terminée avec succès.</b>")
