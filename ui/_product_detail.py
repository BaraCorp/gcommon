#!usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fad

from PyQt4.QtGui import (QHBoxLayout, QGridLayout)
from PyQt4.QtCore import QDate, Qt, QVariant, SIGNAL

from models import (Store, Product)
from Common.ui.common import (FWidget, BttSmall, FLabel)


class InfoTableWidget(FWidget):

    def __init__(self, parent, *args, **kwargs):
        super(FWidget, self).__init__(parent=parent, *args, **kwargs)

        self.parent = parent

        self.refresh()
        self.info_box = FLabel(" ")
        self.image = FLabel(" ")
        self.image_btt = BttSmall("")
        self.image_btt.setFlat(True)
        self.image_btt.clicked.connect(self.show_image)

        hbox = QHBoxLayout()
        gridbox = QGridLayout()
        gridbox.addWidget(self.info_box, 0, 0)
        gridbox.addWidget(self.image, 1, 0)
        gridbox.addWidget(self.image_btt, 1, 1)
        hbox.addLayout(gridbox)
        self.setLayout(hbox)

    def refresh_(self, idd):

        self.prod = Product.get(id=idd)
        rest_by_store = ""

        for store in Store.select():
            remaining, nbr_parts = store.get_remaining_and_nb_parts(self.prod)

            if remaining < 10:
                color_style = 'color: DarkGreen'
            if remaining <= 5:
                color_style = 'color: LightCoral'
            if remaining <= 2:
                color_style = 'color: red; text-decoration: blink'
            if remaining >= 10:
                color_style = 'color: LimeGreen;'
            color_style = color_style + \
                "; border:3px solid green; font-size: 15px"
            if Store.select().count() == 1:
                rest_by_store += """ <p><strong style='{color_style}'> {remaining} </strong><i>pièces</i></p>
                """.format(color_style=color_style, remaining=remaining)
            else:
                rest_by_store += """<li> {store}: <strong style='{color_style}'>
                    {nbr_parts} </strong><i>pièces</i> <b>{remaining} </b><i>carton</i>
                    </li>""".format(store=store.name, color_style=color_style, remaining=remaining,
                                    nbr_parts=nbr_parts * remaining)
        width = height = 50
        if self.prod.image_link:
            self.image_btt.setText("Zoom")
            width = 200
            height = 100

        self.info_box.setText(u"""<h2>{name}</h2>
            <h4>Quantité restante:</h4>
            <ul>{remaining}</ul>
            """.format(name=self.prod.name,
                       remaining=rest_by_store))
        self.image.setText("""<img src="{image}" width='{width}'
            height='{height}'>""".format(image=self.prod.image_link,
                                         width=width, height=height))

    def show_image(self):
        """ afficher l'image complete dans une autre fenetre"""
        from GCommon.ui.show_image import ShowImageViewWidget
        try:
            self.parent.open_dialog(
                ShowImageViewWidget, modal=False, prod=self.prod)
        except AttributeError:
            pass
