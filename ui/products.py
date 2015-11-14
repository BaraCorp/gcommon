#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fad
from __future__ import (unicode_literals, absolute_import, division,
                        print_function)

import os

from PyQt4.QtCore import Qt, SIGNAL, SLOT
from PyQt4.QtGui import (QVBoxLayout, QFileDialog, QGridLayout,
                         QTableWidgetItem, QIcon, QMenu)

from Common.ui.util import raise_error
from Common.exports_xls import export_dynamic_data
from Common.ui.table import FTableWidget
from Common.ui.common import (FWidget, FPageTitle, Button, BttExportXLS)

from GCommon.ui.confirm_deletion import ConfirmDeletionDiag
from GCommon.ui.product_edit_or_add import EditOrAddProductsDialog

from configuration import Config
from models import Product


class ProductsViewWidget(FWidget):

    def __init__(self, product="", parent=0, *args, **kwargs):
        super(ProductsViewWidget, self).__init__(parent=parent, *args,
                                                 **kwargs)

        self.parentWidget().setWindowTitle(Config.APP_NAME +
                                           u"    GESTION ARTICLES")

        self.parent = parent

        vbox = QVBoxLayout()
        gridbox = QGridLayout()
        self.title = u"Liste  d'articles"
        vbox.addWidget(FPageTitle(self.title))

        tablebox = QVBoxLayout()
        # tablebox.addWidget(FPageTitle(u"Tableau Articles"))
        self.table_prod = ProductsTableWidget(parent=self)
        tablebox.addWidget(self.table_prod)

        butt = Button(u"+ &Article")
        butt.clicked.connect(self.add_prod)
        gridbox.addWidget(butt, 0, 2)

        self.export_xls_btt = BttExportXLS(u"Exporter")
        self.connect(self.export_xls_btt, SIGNAL('clicked()'),
                     self.export_xls)
        gridbox.addWidget(self.export_xls_btt, 0, 4)

        gridbox.setColumnStretch(0, 3)
        # gridbox.setRowStretch(0, 1)
        vbox.addLayout(gridbox)
        vbox.addLayout(tablebox)
        self.setLayout(vbox)

    def export_xls(self):
        dict_data = {
            'file_name': "produits.xls",
            'headers': self.table_prod.hheaders,
            'data': self.table_prod.data,
            'sheet': self.title,
            'widths': self.table_prod.stretch_columns
        }
        export_dynamic_data(dict_data)

    def add_prod(self):
        ''' add operation '''
        self.parent.open_dialog(EditOrAddProductsDialog, modal=True,
                                product=None, table_p=self.table_prod)


class ProductsTableWidget(FTableWidget):

    def __init__(self, parent, *args, **kwargs):
        FTableWidget.__init__(self, parent=parent, *args, **kwargs)
        self.parent = parent

        self.hheaders = [u"Categorie", u"Article", u"Quantité(carton)"]
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.popup)

        self.stretch_columns = [1]
        self.align_map = {0: 'l', 1: 'l', 2: 'r'}
        self.display_vheaders = True
        self.sorter = True

        self.refresh_()

    def refresh_(self):
        """ """
        self._reset()
        self.set_data_for()
        self.refresh()

    def set_data_for(self):
        self.data = [(prod.category.name, prod.name, prod.number_parts_box)
                     for prod in Product.select().order_by(Product.name.asc())]

    def popup(self, pos):
        row = self.selectionModel().selection().indexes()[0].row()
        if (len(self.data) - 1) < row:
            return False

        self.product = Product.select().where(
            Product.name == self.data[row][1]).get()
        menu = QMenu()
        menu.addAction(QIcon(u"{}edit.png".format(Config.img_cmedia)),
                       u"modifier", lambda: self.prod_edit(self.product))
        menu.addAction(QIcon("{}del.png".format(Config.img_cmedia)),
                       u"supprimer", lambda: self.prod_del(self.product))

        self.action = menu.exec_(self.mapToGlobal(pos))

    def prod_del(self, product):
        if not product.last_report:
            self.parent.open_dialog(ConfirmDeletionDiag, modal=True,
                                    obj_delete=product,
                                    msg="{}".format(product.display_name()),
                                    table_p=self.parent.table_prod)
        else:
            raise_error(u"Suppresion impossible",
                        u"<h2>Il y a eu au moins un rapport pour cet article"
                        u"</h2></br><i>IL faut les supprimés d'abord</i>")

    def prod_edit(self, product):
        self.parent.open_dialog(EditOrAddProductsDialog,
                                modal=True, product=product,
                                table_p=self.parent.table_prod)

    def _item_for_data(self, row, column, data, context=None):
        return super(ProductsTableWidget, self)._item_for_data(row, column,
                                                               data, context)

    def click_item(self, row, column, *args):
        pass
