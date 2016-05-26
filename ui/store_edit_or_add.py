#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fad

from __future__ import (
    unicode_literals, absolute_import, division, print_function)

from PyQt4.QtCore import Qt
from PyQt4.QtGui import (QIcon, QVBoxLayout, QTableWidgetItem,
                         QDialog, QFormLayout)

from configuration import Config

from Common.ui.common import (FWidget, FPageTitle, Button, IntLineEdit,
                              FLabel, LineEdit, Warning_btt, Button_save)
from Common.ui.util import check_is_empty, field_error
from models import Store
import peewee


class EditOrAddStoresViewWidget(QDialog, FWidget):

    def __init__(self, store, table_p, parent, *args, **kwargs):
        QDialog.__init__(self, parent, *args, **kwargs)

        self.parent = parent
        self.table_p = table_p
        self.store = store

        if store:
            self.title = u"Modification info. magasin {}".format(
                self.store.name)
            self.succes_msg = u"Info. magasin <b>%s</b> a été mise à jour" % self.store.name

        else:
            self.store = Store()
            self.succes_msg = u"Info.magasin a été bien enregistré"
            self.title = u"Ajout de nouvel magasin"

        # self.parentWidget().setWindowTitle(Config.APP_NAME + self.title)
        self.name_field = LineEdit(self.store.name)
        self.stock_maxi_field = IntLineEdit(str(self.store.stock_maxi))

        vbox = QVBoxLayout()
        vbox.addWidget(FPageTitle(self.title))
        formbox = QFormLayout()

        formbox.addRow(FLabel(u"Nom"), self.name_field)
        formbox.addRow(FLabel(u"Quantité maxi"), self.stock_maxi_field)
        butt_cancel = Warning_btt(u"Annuler")
        butt_cancel.clicked.connect(self.cancel)
        butt = Button_save(u"&Enregistrer")
        butt.clicked.connect(self.add_or_edit_prod)
        formbox.addRow(butt_cancel, butt)

        vbox.addLayout(formbox)
        self.setLayout(vbox)

    def cancel(self):
        self.close()

    def is_valide(self):
        if check_is_empty(self.name_field):
            return False
        return True

    def add_or_edit_prod(self):

        if not self.is_valide():
            print("is not valide")
            return

        store = self.store
        store.name = str(self.name_field.text())
        store.stock_maxi = int(self.stock_maxi_field.text())
        try:
            store.save()
            self.cancel()
            self.table_p.refresh_()
            self.parent.Notify(self.succes_msg, "success")
        except peewee.IntegrityError as e:
            field_error(
                self.name_field, u"""Le produit <b>%s</b> existe déjà dans la basse de donnée.""" % store.name)
            return False
