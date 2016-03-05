#!/usr/bin/env python
# -*- coding= UTF-8 -*-
# Fad

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

from models import InvoiceItem
from Common.cel import cel
from configuration import Config
from Common.ui.util import get_temp_filename


def pdFview(filename, invoice):
    """
        cette views est cree pour la generation du PDF
    """

    if not filename:
        filename = get_temp_filename('pdf')
        print(filename)
    #on recupere les items de la facture
    items_invoice = InvoiceItem.filter(invoices=invoice)

    # Static source pdf to be overlayed
    PDFSOURCE = 'fact_source.pdf'
    TMP_FILE = 'tmp.pdf'
    DATE_FORMAT = u"%d/%m/%Y"

    DEFAULT_FONT_SIZE = 11
    FONT = 'Courier-Bold'
    # A simple function to return a leading 0 on any single digit int.

    def double_zero(value):
        try:
            return '%02d' % value
        except TypeError:
            return value

    # setup the empty canvas
    from io import FileIO as file
    # from Common.pyPdf import PdfFileWriter, PdfFileReader
    from PyPDF2 import PdfFileWriter, PdfFileReader

    # PDF en entrée
    input1 = PdfFileReader(file(PDFSOURCE, "rb"))

    # PDF en sortie
    output = PdfFileWriter()
    # Récupération du nombre de pages
    n_pages = input1.getNumPages()
    # Pour chaque page
    for i in range(n_pages):
        # Récupération de la page du doc initial (input1)
        page = input1.getPage(i)

        p = canvas.Canvas(TMP_FILE, pagesize=A4)
        # p.setFont(FONT, DEFAULT_FONT_SIZE)

        p.drawString(130, 683, str(invoice.number))
        p.drawString(98, 667, (invoice.client))

        p.drawString(460, 683, str(invoice.date.strftime(DATE_FORMAT)))

        # On ecrit les invoiceitem
        x, y = 40, 610
        for i in items_invoice:
            p.drawString(x, y, str(i.quantity).rjust(11, ' '))
            p.drawString(x + 75, y, str(i.description))
            p.drawString(x + 340, y, str(i.price).rjust(10, ' '))
            p.drawString(x + 430, y, str(i.price * i.quantity).rjust(10, ' '))
            y -= 20
        # on teste le type
        if invoice.type_ == "Facture":
            p.drawString(59, 80, "Pour acquit: ")
        else:
            p.drawString(59, 80, "Pour acceptation: ")

        p.drawString(435, 80, "Le fournisseur: ")
        #On calcul le montant total hors taxe et sa conversion en lettre
        ht = 0
        for i in items_invoice:
            montant = i.price * i.quantity
            ht += montant

        ht_en_lettre = cel(ht)

        p.drawString(470, 150, str(ht).rjust(10, ' '))
        ht_en_lettre1, ht_en_lettre2 = controle_caratere(ht_en_lettre +
                                                        " FCFA", 46, 40)
        p.drawString(258, 116, (ht_en_lettre  + " FCFA"))
        # p.drawString(258, 116, (ht_en_lettre1))
        # p.drawString(53, 100, (ht_en_lettre2))

        # legal_infos, legal_infos1 = controle_caratere(Config.BP, 55, 55)
        # p.drawString(90, 14, legal_infos)
        # p.drawString(90, 6, legal_infos1)
        p.showPage()
        # Sauvegarde de la page
        p.save()
        # Création du watermark
        watermark = PdfFileReader(file(TMP_FILE, "rb"))
        # Création page_initiale+watermark
        page.mergePage(watermark.getPage(0))
        # Création de la nouvelle page
        output.addPage(page)
    # Nouveau pdf
    file_dest = filename + ".pdf"
    outputStream = file(file_dest, u"wb")
    output.write(outputStream)
    outputStream.close()

    return file_dest


def controle_caratere(lettre, nb_controle, nb_limite):
    """
        cette fonction decoupe une chaine de caratere en fonction
        du nombre de caratere donnée et conduit le reste à la ligne
    """
    lettre = lettre
    if len(lettre) <= nb_controle:
        ch = lettre
        ch2 = u""
        return ch, ch2
    else:
        ch = ch2 = u""
        for n in lettre.split(u" "):
            if len(ch) <= nb_limite:
                ch = ch + u" " + n
            else:
                ch2 = ch2 + u" " + n
        return ch, ch2
