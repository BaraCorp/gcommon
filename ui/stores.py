#!usr/bin/env python
# -*- encoding: utf-8 -*-
# maintainer: Fad
from __future__ import (
    unicode_literals, absolute_import, division, print_function)

from PyQt4.QtCore import Qt, SIGNAL
from PyQt4.QtGui import (QVBoxLayout, QGridLayout, QIcon, QMenu)

from Common.ui.common import (FWidget, FPageTitle, FBoxTitle, Button,
                              IntLineEdit, LineEdit,
                              BttExportXLS)
from Common.ui.util import raise_error
from Common.ui.table import FTableWidget

from configuration import Config

from GCommon.ui.confirm_deletion import ConfirmDeletionDiag
from GCommon.ui.store_edit_or_add import EditOrAddStoresViewWidget

from models import Store


class StoresViewWidget(FWidget):

    def __init__(self, store="", parent=0, *args, **kwargs):
        super(StoresViewWidget, self).__init__(parent=parent,
                                               *args, **kwargs)
        self.parentWidget().setWindowTitle(Config.APP_NAME + u"  MAGASINS")

        self.parent = parent

        vbox = QVBoxLayout()
        self.title = u"Liste magasins"
        vbox.addWidget(FPageTitle(self.title))

        tablebox = QVBoxLayout()
        tablebox.addWidget(FBoxTitle(u"Tableau magasins"))
        self.store_table = StoresTableWidget(parent=self)
        tablebox.addWidget(self.store_table)

        formbox = QVBoxLayout()
        gridbox = QGridLayout()

        self.name = LineEdit()
        self.stock_maxi = IntLineEdit()

        butt = Button(u"+ &Magasin")
        butt.clicked.connect(self.add_store)
        gridbox.addWidget(butt, 0, 2)

        self.export_xls_btt = BttExportXLS(u"Exporter")
        self.connect(self.export_xls_btt, SIGNAL('clicked()'),
                     self.export_xlsx)
        gridbox.addWidget(self.export_xls_btt, 0, 4)

        gridbox.setColumnStretch(0, 3)
        formbox.addLayout(gridbox)

        vbox.addLayout(formbox)
        vbox.addLayout(tablebox)
        self.setLayout(vbox)

    def export_xlsx(self):
        from Common.exports_xlsx import export_dynamic_data
        dict_data = {
            'file_name': "produits.xls",
            'headers': self.store_table.hheaders,
            'data': self.store_table.data,
            'sheet': self.title,
            'widths': self.store_table.stretch_columns
        }
        export_dynamic_data(dict_data)

    def add_store(self):
        ''' add operation '''
        self.parent.open_dialog(EditOrAddStoresViewWidget, modal=True,
                                store=None, table_p=self.store_table)


class StoresTableWidget(FTableWidget):

    def __init__(self, parent, *args, **kwargs):
        FTableWidget.__init__(self, parent=parent, *args, **kwargs)
        self.parent = parent

        self.hheaders = [u"Nom", u"Quantité maxi"]
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.popup)

        self.set_data_for()
        self.stretch_columns = [0, 1]
        self.align_map = {0: 'l'}
        # self.max_rows = 100
        self.display_vheaders = False
        self.refresh()

    def refresh_(self):
        """ """
        self._reset()
        self.set_data_for()
        self.refresh()

    def set_data_for(self):
        self.data = [(mag.name, mag.stock_maxi)
                     for mag in Store.select().order_by(Store.id.desc())]

    def popup(self, pos):
        row = self.selectionModel().selection().indexes()[0].row()
        if (len(self.data) - 1) < row:
            return False

        self.store = Store.select().where(
            Store.name == self.data[row][0]).get()
        menu = QMenu()
        menu.addAction(QIcon(u"{}edit.png".format(Config.img_cmedia)),
                       u"modifier", lambda: self.prod_edit(self.store))
        menu.addAction(QIcon("{}del.png".format(Config.img_cmedia)),
                       u"supprimer", lambda: self.prod_del(self.store))

        self.action = menu.exec_(self.mapToGlobal(pos))

    def prod_del(self, store):
        if not store.get_report_or_none():
            self.parent.open_dialog(ConfirmDeletionDiag, modal=True,
                                    obj_delete=store,
                                    msg="{}".format(store.name),
                                    table_p=self.parent.store_table)
        else:
            raise_error(u"Suppresion impossible",
                        u"<h2>Il y a eu au moins un rapport dans ce magasin"
                        u"</h2></br><i>IL faut les supprimés d'abord</i>")

    def prod_edit(self, store):
        self.parent.open_dialog(EditOrAddStoresViewWidget, modal=True,
                                store=store, table_p=self.parent.store_table)

    def _item_for_data(self, row, column, data, context=None):
        return super(StoresTableWidget, self)._item_for_data(row, column,
                                                             data, context)
