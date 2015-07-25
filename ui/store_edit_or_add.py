#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fad

from __future__ import (unicode_literals, absolute_import, division, print_function)

import sqlite3

from PyQt4.QtCore import Qt
from PyQt4.QtGui import (QIcon, QVBoxLayout, QTableWidgetItem,
                         QDialog, QFormLayout)

from configuration import Config
from Common.ui.common import (FWidget, FPageTitle, Button, IntLineEdit,
                              FLabel, LineEdit, Warning_btt, Button_save)
from Common.ui.util import raise_success
from models import Store


class EditOrAddStoresViewWidget(QDialog, FWidget):
    def __init__(self, store, table_p, parent, *args, **kwargs):
        QDialog.__init__(self, parent, *args, **kwargs)

        self.parent = parent
        self.table_p = table_p
        self.store = store

        if store:
            self.title = u"Modification info. magasin {}".format(self.store.name)
            self.succes_msg = u"Info. magasin <b>%s</b> a été mise à jour" % self.store.name

        else:
            self.store = Store()
            self.succes_msg = u"Info.magasin a été bien enregistré"
            self.title = u"Ajout de nouvel magasin"

        # self.parentWidget().setWindowTitle(Config.APP_NAME + self.title)
        self.name = LineEdit(self.store.name)
        self.stock_maxi = IntLineEdit(str(self.store.stock_maxi))

        vbox = QVBoxLayout()
        vbox.addWidget(FPageTitle(self.title))
        formbox = QFormLayout()

        formbox.setFieldGrowthPolicy(formbox.ExpandingFieldsGrow)
        formbox.setRowWrapPolicy(formbox.WrapLongRows)
        formbox.setContentsMargins(-1, -1, 9, -1)
        formbox.setLabelAlignment(Qt.AlignTrailing|Qt.AlignVCenter)
        formbox.setFormAlignment(Qt.AlignTrailing|Qt.AlignTop|Qt.AlignTrailing)
        # formbox.setHorizontalSpacing(222)
        formbox.setVerticalSpacing(8)
        formbox.addRow(FLabel(u"Nom"), self.name)
        formbox.addRow(FLabel(u"Quantité maxi"), self.stock_maxi)
        butt_cancel = Warning_btt(u"Annuler")
        butt_cancel.clicked.connect(self.cancel)
        butt = Button_save(u"&Enregistrer")
        butt.clicked.connect(self.add_or_edit_prod)
        formbox.addRow(butt_cancel, butt)

        vbox.addLayout(formbox)
        self.setLayout(vbox)

    def cancel(self):
        self.close()

    def add_or_edit_prod(self):

        name = str(self.name.text())
        stock_maxi = int(self.stock_maxi.text())

        self.name.setStyleSheet("")
        self.stock_maxi.setStyleSheet("")
        if stock_maxi == "":
            self.stock_maxi.setStyleSheet("background-color: "
                                           "rgb(255, 235, 235);")
            self.stock_maxi.setToolTip(u"Ce champs est obligatoire.")
            return False
        if name == "":
            self.name.setStyleSheet("background-color: "
                                           "rgb(255, 235, 235);")
            self.name.setToolTip(u"Ce champs est obligatoire.")
            return False

        store = self.store
        store.name = name
        store.stock_maxi = stock_maxi
        try:
            store.save()
            self.cancel()
            self.table_p.refresh_()
            self.parent.Notify(self.succes_msg)

        except sqlite3.IntegrityError as e:
            err = u"%s" % e
            if u"name" in err:
                self.name.setStyleSheet("background-color: "
                                               "rgb(255, 235, 235);")
                self.name.setToolTip(u"Le produit %s "
                                        u"existe déjà dans la basse de "
                                        u"donnée." % store.name)
                return False
            if u"stock_maxi" in err:
                self.code.setStyleSheet("background-color: "
                                               "rgb(255, 235, 235);")
                self.code.setToolTip(u"Le code %s "
                                        u"existe déjà dans la basse de "
                                        u"donnée." % store.stock_maxi)
                return False
