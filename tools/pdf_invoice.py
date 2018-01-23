#!/usr/bin/env python
# -*- coding= UTF-8 -*-
# Fad

import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# from reportlab.pdfbase import pdfmetrics
# from reportlab.pdfbase.ttfonts import TTFont

# setup the empty canvas
from io import FileIO as file
# from Common.pyPdf import PdfFileWriter, PdfFileReader
from PyPDF2 import PdfFileWriter, PdfFileReader
from models import Report
from num2words import num2words
from configuration import Config
from Common.ui.util import get_temp_filename, formatted_number, device_amount


def pdf_view(filename, invoice):
    """
        cette views est cree pour la generation du PDF
    """

    if not filename:
        filename = get_temp_filename('pdf')
        # print(filename)
    # on recupere les items de la facture
    items_invoice = Report.filter(invoice=invoice)
    # Static source pdf to be overlayed
    PDFSOURCE = Config.INV_TEMPLATE_PDF
    TMP_FILE = os.path.join(Config.ROOT_DIR, 'tmp.pdf')
    DATE_FORMAT = u"%d/%m/%Y"
    DEFAULT_FONT_SIZE = 11
    FONT = 'Times-Roman'

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
        p.setFont(FONT, DEFAULT_FONT_SIZE)
        p.drawString(115, 639, str(invoice.number))
        p.drawString(82, 625, (invoice.client.name))
        p.drawString(445, 625, str(invoice.date.strftime(DATE_FORMAT)))
        # On ecrit les invoiceitem
        x, y = 122, 574
        x_qty = x
        x_description = x + 10
        x_price = x + 340
        x_amount = x + 433

        for i in items_invoice:
            p.drawRightString(x_qty, y, str(i.qty))
            p.drawString(x_description, y, str(i.product.name))
            p.drawRightString(x_price, y, str(
                formatted_number(i.selling_price)))
            p.drawRightString(x_amount, y, str(formatted_number(
                i.selling_price * i.qty)))
            y -= 17
        # On calcul le montant total hors taxe et sa conversion en lettre
        ht = sum([(val.selling_price * val.qty) for val in items_invoice])
        tax_rate = invoice.tax_rate if invoice.tax else 0
        mt_tax = int((ht * tax_rate) / 100)
        htt = mt_tax + ht
        ht_en_lettre = num2words(ht, lang="fr")
        ht_en_lettre1, ht_en_lettre2 = controle_caratere(
            ht_en_lettre + " francs CFA", 50, 50)
        p.drawString(260, 191, (ht_en_lettre1))
        p.drawString(50, 175, (ht_en_lettre2))
        p.setFont('Times-Bold', 11)
        p.drawString(52, 639, "Facture N° :")
        p.drawString(x_price - 20, 248, str(tax_rate) + "%")
        # TVA
        p.drawRightString(x_amount, 248, device_amount(mt_tax))
        # Hors Taxe
        p.drawRightString(x_amount, 265, str(device_amount(ht)))
        # Tout Taxe
        p.drawRightString(x_amount, 232, str(device_amount(htt)))
        x_foot = 145
        p.drawString(50, x_foot, "Acceptation" if invoice.type_ ==
                     "Proforma" else "Acquit")
        p.drawString(490, x_foot, "Fournisseur")
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
    try:
        outputStream = file(file_dest, u"wb")
        output.write(outputStream)
        outputStream.close()
        return file_dest
    except OSError as e:
        from Common.ui.util import raise_error
        raise_error(u"Impossible de lancer le PDF", """
                    Car un autre en cours d'utilistation. Kill le \n{}""".format(e))
        return


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
