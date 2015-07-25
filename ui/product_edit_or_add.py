#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fad
from __future__ import (unicode_literals, absolute_import, division, print_function)

import os
import sqlite3

from PyQt4.QtCore import Qt
from PyQt4.QtGui import (QIcon, QVBoxLayout, QFileDialog, QDialog,
                         QIntValidator, QFormLayout, QPushButton, QCompleter)

from configuration import Config

from Common.ui.util import raise_error, import_file
from Common.ui.common import (FWidget, FPageTitle, Button_save, FormLabel,
                              FLabel, LineEdit, IntLineEdit, Warning_btt)
from models import Category, Product, FileJoin


class EditOrAddProductsDialog(QDialog, FWidget):

    def __init__(self, product, table_p, parent, *args, **kwargs):
        QDialog.__init__(self, parent, *args, **kwargs)

        self.table_p = table_p
        self.prod = product
        self.parent = parent

        if self.prod:
            self.title = u"Modification de l'article {}".format(self.prod.name)
            # namefile = self.prod.file_join.get(file_slug , "Aucune")
            try:
                namefile = self.prod.file_join.file_name
            except:
                namefile = "Aucune"
            self.succes_msg = u"L'article <b>%s</b> a été mise à jour" % self.prod.name
        else:
            self.succes_msg = u"L'article a été bien enregistré"
            namefile = "..."
            self.title = u"Ajout de nouvel article"
            self.prod = Product()

        self.setWindowTitle(self.title)

        # self.code = LineEdit(self.prod.code)
        self.name = LineEdit(self.prod.name)
        try:
            self.category_name = Category.select().where(Category.name==self.prod.category.name).get().name
        except:
            self.category_name = ""
        self.category = LineEdit(self.category_name)

        self.number_parts_box = IntLineEdit(str(self.prod.number_parts_box))
        self.number_parts_box.setValidator(QIntValidator())

        completion_values =  [catg.name for catg in Category.all()]
        completer = QCompleter(completion_values, parent=self)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
        self.category.setCompleter(completer)

        vbox = QVBoxLayout()
        formbox = QFormLayout()
        formbox.setFieldGrowthPolicy(formbox.ExpandingFieldsGrow)
        formbox.setRowWrapPolicy(formbox.WrapLongRows)
        formbox.setContentsMargins(-1, -1, 9, -1)
        formbox.setLabelAlignment(Qt.AlignTrailing|Qt.AlignVCenter)
        formbox.setFormAlignment(Qt.AlignTrailing|Qt.AlignTop|Qt.AlignTrailing)
        # formbox.setHorizontalSpacing(222)
        formbox.setVerticalSpacing(8)
        formbox.addRow(FLabel(u"Désignation"), self.name)
        formbox.addRow(FLabel(u"Categorie"), self.category)
        formbox.addRow(FLabel(u"Number pieces carton"), self.number_parts_box)
        self.path_ = FormLabel(namefile)
        butt_parco = QPushButton(QIcon.fromTheme('document-open', QIcon('')), "")
        butt_parco.clicked.connect(self.import_image)
        butt_cancel = Warning_btt(u"Annuler")
        butt_cancel.clicked.connect(self.cancel)
        formbox.addRow(FLabel(u"Image"), butt_parco)
        formbox.addRow("", self.path_)
        butt = Button_save(u"&Enregistrer")
        butt.clicked.connect(self.add_or_edit_prod)
        formbox.addRow(butt_cancel, butt)

        vbox.addLayout(formbox)
        self.setLayout(vbox)

    def import_image(self):
        """ """
        self.path_filename = QFileDialog.getOpenFileName(self, "Open Image", "",
            "Documents ({})".format(Config.DOC_SUPPORT),)
        if self.path_filename:
            self.name_file = str(os.path.basename(u"{}".format(self.path_filename)))
            self.path_.setText(self.name_file)

    def cancel(self):
        self.close()

    def add_or_edit_prod(self):

        name = str(self.name.text())
        # code = str(self.code.text())
        category = str(self.category.text())
        number_parts_box = str(self.number_parts_box.text())

        self.name.setStyleSheet("")
        # self.code.setStyleSheet("")
        self.number_parts_box.setStyleSheet("")
        if name == "":
            self.name.setStyleSheet("background-color: rgb(255, 235, 235);")
            self.name.setToolTip(u"Ce champs est obligatoire.")
            return False

        product = self.prod
        # product.code_prod = code if code != "" else None
        product.name = name
        product.number_parts_box = number_parts_box
        # prev_image = str(self.prod.file_slug)
        product.category = Category.get_or_create(category)

        try:
            product.file_join = FileJoin(file_name=self.name_file,
                    file_slug=import_file(str(self.path_filename),
                                                  self.name_file)).save()
        except IOError:
            raise_error(u"Problème d'import du fichier",
                        u"Changer le nom du fichier et reesayé \n \
                        si ça ne fonctionne pas contacté le developper")
            return
        except AttributeError:
            pass

        try:
            product.save()
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
                                        u"donnée." % product.name)
                return False
            if u"code_prod" in err:
                self.code.setStyleSheet("background-color: "
                                               "rgb(255, 235, 235);")
                self.code.setToolTip(u"Le code %s "
                                        u"existe déjà dans la basse de "
                                        u"donnée." % product.code_prod)
                return False
