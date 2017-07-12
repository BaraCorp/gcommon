#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fad
from __future__ import (
    unicode_literals, absolute_import, division, print_function)

import os
import peewee

from PyQt4.QtCore import Qt
from PyQt4.QtGui import (QIcon, QVBoxLayout, QFileDialog, QDialog,
                         QIntValidator, QFormLayout, QPushButton, QCompleter)

from configuration import Config

from Common.ui.util import check_is_empty, field_error
from Common.ui.common import (FWidget, Button_save,
                              FLabel, LineEdit, IntLineEdit, Warning_btt)

from models import Category, Product, FileJoin


class EditOrAddProductsDialog(QDialog, FWidget):

    def __init__(self, table_p, parent, product=None, *args, **kwargs):
        QDialog.__init__(self, parent, *args, **kwargs)

        self.table_p = table_p
        self.prod = product
        self.parent = parent
        self.filename = "Parcourire ..."
        self.path_filename = None

        if self.prod:
            self.title = u"Modification de l'article {}".format(self.prod.name)
            self.succes_msg = u"L'article <b>%s</b> a été mise à jour" % self.prod.name
            try:
                self.filename = self.prod.file_join.file_name
            except:
                pass
        else:
            self.succes_msg = u"L'article a été bien enregistré"
            self.title = u"Ajout de nouvel article"
            self.prod = Product()

        self.setWindowTitle(self.title)

        # self.code = LineEdit(self.prod.code)
        self.name_field = LineEdit(self.prod.name)
        try:
            self.category_name = Category.select().where(
                Category.name == self.prod.category.name).get().name
        except:
            self.category_name = ""
        self.category_field = LineEdit(self.category_name)

        self.number_parts_box_field = IntLineEdit(
            str(self.prod.number_parts_box))
        self.number_parts_box_field.setValidator(QIntValidator())

        completion_values = [catg.name for catg in Category.all()]
        completer = QCompleter(completion_values, parent=self)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
        self.category_field.setCompleter(completer)

        vbox = QVBoxLayout()
        formbox = QFormLayout()
        formbox.addRow(FLabel(u"Nom"), self.name_field)
        formbox.addRow(FLabel(u"Categorie"), self.category_field)
        formbox.addRow(
            FLabel(u"Quantité (carton)"), self.number_parts_box_field)
        self.butt_parco = QPushButton(
            QIcon.fromTheme('document-open', QIcon('')), self.filename)
        self.butt_parco.clicked.connect(self.import_image)
        butt_cancel = Warning_btt(u"Annuler")
        butt_cancel.clicked.connect(self.cancel)
        formbox.addRow(FLabel(u"Image"), self.butt_parco)
        butt = Button_save(u"&Enregistrer")
        butt.clicked.connect(self.add_or_edit_prod)
        formbox.addRow(butt_cancel, butt)

        vbox.addLayout(formbox)
        self.setLayout(vbox)

    def import_image(self):

        self.path_filename = QFileDialog.getOpenFileName(
            self, "Open Image", "", "Image Files ({})".format(
                Config.DOC_SUPPORT),)
        if self.path_filename:
            self.fileName = str(
                os.path.basename(u"{}".format(self.path_filename)))
            self.butt_parco.setText(self.fileName)

    def cancel(self):
        self.close()

    def is_valide(self):
        flag = True
        if (check_is_empty(self.name_field) or
                check_is_empty(self.category_field)
                or check_is_empty(self.number_parts_box_field)):
            flag = False
        return flag

    def add_or_edit_prod(self):

        if not self.is_valide():
            print("is not valide")
            return

        name = str(self.name_field.text())
        category = str(self.category_field.text())
        number_parts_box = str(self.number_parts_box_field.text())

        product = self.prod
        product.name = name
        product.number_parts_box = number_parts_box
        product.category = Category.get_or_create(category)

        try:
            if self.path_filename:
                fileobj = FileJoin(file_name=self.fileName,
                                   file_slug=self.path_filename)
                fileobj.save()
                product.file_join = fileobj
        except IOError:
            self.parent.Notify(u"""<h2>Problème d'import du fichier</h2>
                Changer le nom du fichier et reesayé si ça ne fonctionne pas contacté le developper""", "error")
            return
        except Exception as e:
            print(e)

        try:
            product.save()
            self.cancel()
            self.table_p.refresh_()
            self.parent.Notify(self.succes_msg, "success")
        except peewee.IntegrityError as e:
            field_error(
                self.name_field, u"""Le produit <b>%s</b> existe déjà dans la basse de donnée.""" % product.name)
            return False
