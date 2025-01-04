from pathlib import Path
import os
import pandas as pd
import datetime as dt
# from docxtpl import DocxTemplate
# import openpyxl
# from docx.enum.table import WD_TABLE_ALIGNMENT
# from docx import Document
# from docx.shared import Cm
# import numpy as np
# from datetime import date
# import datetime as dt
# from PyInquirer import prompt
# import pprint
# import tkinter as tk

def produce_sepa_export_dfs(invoices_selected_persons,mandates,creditor_ID):
    debit = invoices_selected_persons[(invoices_selected_persons["Dokumenttyp"] == "Rechnung")]
    transfer = invoices_selected_persons[(invoices_selected_persons["Dokumenttyp"] == "Gutschrift")|(invoices_selected_persons["Dokumenttyp"] == "Information")]
    debitdoubles = debit["Empfänger Name"][debit["Empfänger Name"].isin(transfer["Empfänger Name"])].index
    transferdoubles = transfer["Empfänger Name"][transfer["Empfänger Name"].isin(debit["Empfänger Name"])].index
    doublesprocess = {"Name":[],"Debit":[],"Transfer":[],"Type":[],"Final":[]}
    for i,j in zip(debitdoubles,transferdoubles):
        doublesprocess["Name"].append(debit.loc[i,"Empfänger Name"])
        doublesprocess["Debit"].append(debit.loc[i,"Rechnungsbetrag Brutto"])
        doublesprocess["Transfer"].append(transfer.loc[j,"Rechnungsbetrag Brutto"])
        if debit.loc[i,'Rechnungsbetrag Brutto'] < transfer.loc[j,'Rechnungsbetrag Brutto']:
            finalsum = transfer.loc[j,'Rechnungsbetrag Brutto'] - debit.loc[i,'Rechnungsbetrag Brutto']
            transfer.loc[j, 'Rechnungsbetrag Brutto'] = finalsum
            debit = debit.drop(i)
            doublesprocess["Type"].append("Überweisung")
            doublesprocess["Final"].append(finalsum)

        else:
            finalsum = debit.loc[i,'Rechnungsbetrag Brutto'] - transfer.loc[j,'Rechnungsbetrag Brutto']
            debit.loc[i, 'Rechnungsbetrag Brutto'] = finalsum
            transfer = transfer.drop(j)
            doublesprocess["Type"].append("Lastschrift")
            doublesprocess["Final"].append(finalsum)


    def create_one_line_debit(invoicelistline,creditor_ID,mandates,type = debit):
        print(invoicelistline["Empfänger Name"])
        columns_debit_export = ['Fälligkeitsdatum', 'Zahlungspflichtiger Name',
       'Zahlungspflichtiger Adresse', 'Zahlungspflichtiger Ort',
       'Zahlungspflichtiger IBAN', 'Zahlungspflichtiger BIC', 'Betrag in EUR',
       'Zahlungsreferenz/Verwendungszweck', 'Auftraggeberinformation',
       'Geschäftsvorfallcode', 'Auftraggeber IBAN',
       'Abweichender Auftraggeber', 'Mandatsausstellungsdatum', 'Creditor ID',
       'Mandatsreferenz', 'Art der Verwendung', 'Firmenlastschrift']

        columns_transfer_export = ['Durchführungsdatum', 'Empfänger Name', 'Empfänger Adresse',
       'Empfänger Ort', 'Empfänger IBAN', 'Empfänger BIC', 'Betrag in EUR',
       'Zahlungsreferenz/Verwendungszweck', 'Auftraggeberinformation',
       'Geschäftsvorfallcode', 'Dringlichkeit', 'Auftraggeber IBAN',
       'Abweichender Auftraggeber']
        if type == "debit":
            exportline = pd.Series([""] * len(columns_debit_export), index=columns_debit_export)
            exportline["Fälligkeitsdatum"] = dt.datetime.today().strftime("%d.%m.%Y")
            matchingdictinvoice = {
                "Zahlungspflichtiger Name": "Empfänger Name",
                "Zahlungspflichtiger Adresse": "Empfänger Adresse 1",
                "Zahlungspflichtiger Ort": "Empfänger Adresse 2",
                "Zahlungspflichtiger IBAN": "Empfänger Konto IBAN",
                "Betrag in EUR": "Rechnungsbetrag Brutto",
                "Auftraggeber IBAN": "Ersteller IBAN"
            }
            exportline["Mandatsreferenz"] = f"{invoicelistline['Empfänger Mitgliedsnummer']:03}"
            exportline["Creditor ID"] = creditor_ID


            mandateline = mandates.data[(mandates.data["Vorname"] == invoicelistline["Empfänger Vorame"])]
            matchingmandate = True
            if not pd.isna(invoicelistline["Empfänger Nachname"]):
                mandateline = mandateline[(mandateline["Nachname"] == invoicelistline["Empfänger Nachname"])]
            if mandateline.size > 0:
                exportline["Mandatsausstellungsdatum"] = mandateline["Mandatsausstellungsdatum"].iloc[0].strftime("%d.%m.%Y")
                exportline["Firmenlastschrift"] = mandateline["Firmenlastschrift"].iloc[0]
            else:
                exportline["Creditor ID"] = 0
                matchingmandate = False


        elif type == "transfer":
            exportline = pd.Series([""] * len(columns_transfer_export), index=columns_transfer_export)
            exportline["Durchführungsdatum"] = dt.datetime.today().strftime("%d.%m.%Y")
            matchingdictinvoice = {
                "Empfänger Name": "Empfänger Name",
                "Empfänger Adresse": "Empfänger Adresse 1",
                "Empfänger Ort": "Empfänger Adresse 2",
                "Empfänger IBAN": "Empfänger Konto IBAN",
                "Betrag in EUR": "Rechnungsbetrag Brutto",
                "Auftraggeber IBAN": "Ersteller IBAN"
            }

        for exportcol in matchingdictinvoice.keys():
            exportline[exportcol] = invoicelistline[matchingdictinvoice[exportcol]]
        exportline["Betrag in EUR"] = f"{exportline['Betrag in EUR']:.2f}".replace('.', ',')


        def get_quartal_out_of_str(string):
            y = (string.split("-"))
            return y[1], y[2]

        year, quartal = get_quartal_out_of_str(invoicelistline["Abrechnung"])
        exportline["Zahlungsreferenz/Verwendungszweck"] = f"Gemeinwohlenergie Rechung {year} Quartal {quartal}"
        if type == "debit":
            return exportline, matchingmandate
        else:
            return exportline


    serieslist = []
    missingmandates = []
    for index, line in debit.iterrows():
        exportline,matchingmandate = create_one_line_debit(line,creditor_ID,mandates,type="debit")
        if exportline is not None:
            serieslist.append(exportline)
            if not matchingmandate:
                missingmandates.append(f"{line['Empfänger Vorame']} {line['Empfänger Nachname']}")
    if len(serieslist) > 1:
        debitexport = pd.concat(serieslist, axis=1).T
    elif len(serieslist) == 1:
        debitexport = serieslist[0].to_frame()
    else: debitexport = None

    serieslist = []
    for index, line in transfer.iterrows():
        exportline = create_one_line_debit(line,creditor_ID,mandates,type="transfer")
        if exportline is not None:
            serieslist.append(exportline)
    if len(serieslist) > 1:
        transferexport = pd.concat(serieslist, axis=1).T
    elif len(serieslist) == 1:
        transferexport = serieslist[0].to_frame()
    else: transferexport = None
    return debitexport,transferexport, missingmandates, doublesprocess

