from nc_py_api import Nextcloud
import pandas as pd
from subwindows import LoginPrompt, Subwindow, MailSelection
from PyQt5 import QtWidgets, QtGui, QtCore
import sys
from PyQt5.QtWidgets import QLabel, QFileDialog, QMessageBox, QGridLayout, QTableWidget, QTableWidgetItem, QListWidget, QWidget, QListWidgetItem, QCheckBox, QListWidgetItem, QPushButton, QVBoxLayout
from importing import mandates,invoices,emails, newmember, load_filepath
from exporting import produce_sepa_export_dfs
from PyQt5.QtWidgets import QHBoxLayout






class TableView(QtWidgets.QTableWidget):
    def __init__(self, data={"1":[0]}, *args):
        QtWidgets.QTableWidget.__init__(self, *args)
        self.data = data
        self.setData()
        self.resizeColumnsToContents()
        self.resizeRowsToContents()
    def set_new_data(self,data):
        """
        sets the Table to new data
        :param data: pd.Dataframe
        :return:
        """
        self.data = data.to_dict(orient="list")
        self.setData(data.shape[0],data.shape[1])
    def setData(self,rowcount = 0, colcount = 0):
        self.setColumnCount(colcount)
        self.setRowCount(rowcount)
        horHeaders = []
        for n, key in enumerate(self.data.keys()):
            horHeaders.append(key)
            for m, item in enumerate(self.data[key]):
                newitem = QtWidgets.QTableWidgetItem(str(item))
                self.setItem(m, n, newitem)
        self.setHorizontalHeaderLabels(horHeaders)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        print("Initializing Window")
        self.setWindowTitle("Faktura Infinity Addon")
        self.resize(1000, 600)
        self.move(20, 20)
        self.second_window = None
        self.exportwindow = None
        self.loaded_filepaths = pd.DataFrame({"Daten":["Mandate","Rechnungsdaten"],
                                  "Speicherort":["",""],

                                              })
        # promptwindows
        self.loginprompt = None
        self.mailselectionprompt = None

        self.creditor_ID = ""
        self.mandatesdata_loaded = False
        self.invoicesdata_loaded = False
        self.init_Ui()
        self.init_data()

    def init_Ui(self):
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget = QtWidgets.QWidget(self)
        self.overallverticallayout = QtWidgets.QVBoxLayout(self.centralwidget)
        menubar = QtWidgets.QMenuBar()
        self.menubardata_Infinity= self.init_menubardata_mandates()
        if self.menubardata_Infinity:
            self.actionFile = menubar.addMenu("Infinity export")
            for menuline in self.menubardata_Infinity:
                action = QtWidgets.QAction(menuline[0], self)
                action.triggered.connect(menuline[2])
                if menuline[1]:
                    action.setShortcut(menuline[1])
                self.actionFile.addAction(action)
            self.actionFile.addSeparator()
            quit = QtWidgets.QAction("Schließen", self)
            quit.setShortcut("Alt+F4")
            quit.triggered.connect(lambda: sys.exit(0))
            self.actionFile.addAction(quit)


        self.overallverticallayout.addWidget(menubar)

        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.verticalLayout0 = QtWidgets.QVBoxLayout() 
        self.verticalLayout1 = QtWidgets.QVBoxLayout()
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.verticalLayout0 = QtWidgets.QVBoxLayout()  # layout on the left with the masslist, and other stuff
        self.verticalLayout1 = QtWidgets.QVBoxLayout()  # laout on the right with the graph
        self.table_0_0 = TableView()
        self.table_0_1 = TableView()
        self.table_1_0 = TableView()
        self.table_1_1 = TableView()
        self.table_1_1.set_new_data(self.loaded_filepaths)
        self.horizontalLayout.addLayout(self.verticalLayout1)
        self.horizontalLayout.addLayout(self.verticalLayout0)
        self.verticalLayout0.addWidget(QLabel("Rechnungsdaten KonsumentInnen"))
        self.verticalLayout0.addWidget(self.table_0_0)
        self.verticalLayout0.addWidget(QLabel("Mandatsdaten KonsumentInnen"))
        self.verticalLayout0.addWidget(self.table_0_1)
        self.verticalLayout0.setStretch(1, 7)
        self.verticalLayout0.setStretch(3, 7)

        self.verticalLayout1.addWidget(QLabel("Rechnungsdaten ProduzentInnen"))
        self.verticalLayout1.addWidget(self.table_1_0)
        self.verticalLayout1.addWidget(QLabel("Dateien geladen:"))
        self.verticalLayout1.addWidget(self.table_1_1)
        self.verticalLayout1.setStretch(1, 7)
        self.verticalLayout1.setStretch(3, 4)

        self.overallverticallayout.addLayout(self.horizontalLayout)



        self.overallverticallayout.addLayout(self.horizontalLayout)
        self.setCentralWidget(self.centralwidget)

    def init_data(self):
        self.mandates = mandates
        self.invoices = invoices
        self.emails = emails
        self.new_member = newmember
    
    def init_menubardata_mandates(self):

        def updatetable_1_1():
            self.table_1_1.set_new_data(self.loaded_filepaths.iloc[0:3])

        def import_mandates(filepath = ''):
            def load_mandate(filepath, nc_loading=False, nc_instance=""):
                if filepath is not None:
                    mandatedata = self.mandates.load_data(filepath=filepath, nc=nc_loading, nc_instance=nc_instance)
                    if mandatedata is not None:
                        self.reload_table_view("0_1", mandatedata)
                        self.loaded_filepaths.loc[self.loaded_filepaths["Daten"][
                            self.loaded_filepaths["Daten"] == "Mandate"].index, "Speicherort"] = filepath
                        updatetable_1_1()
                        self.mandatesdata_loaded = True
                else:
                    return None
            # filepath = "/home/leander/gei/export_infinity/lastschriftmandate.xlsx"
            filepath=""
            if not filepath:
                print("Import mandates")
                filepath = load_filepath(self,"Lade Daten von SEPA Mandate")
                load_mandate(filepath)
            else:
                load_mandate(filepath)

        def import_invoice_data():
            print("import invoice data")
            # filepath = "/home/leander/gei/faktura/pythonProject/data/CC100438_abrechnung_final.xlsx"
            filepath = load_filepath(self,"Importiere Rechnungen von EEG Faktura")
            if filepath is not None:
                self.loaded_filepaths.loc[self.loaded_filepaths["Daten"][self.loaded_filepaths["Daten"] == "Rechnungsdaten"].index, "Speicherort"] = filepath


                invoicedata = self.invoices.load_data(filepath=filepath)
                if invoicedata is not None:
                    debit = invoicedata["list"][(invoicedata["list"]["Dokumenttyp"] == "Rechnung")]
                    transfer = invoicedata["list"][(invoicedata["list"]["Dokumenttyp"] == "Gutschrift")|(invoicedata["list"]["Dokumenttyp"] == "Information")]

                    self.reload_table_view("0_0",debit)
                    self.reload_table_view("1_0",transfer)

                    updatetable_1_1()
                    self.invoicesdata_loaded = True
                else:
                    print()

        def select_templates():
            print("Select templates")
            filepath1 = load_filepath(self,"Wähle Exportvorlage für SEPA Lastschrift aus",filter =  "csv (*.csv)")
            if filepath1 is not None:
                filepath2 = load_filepath(self,"Wähle Exportvorlage für SEPA Lastschrift aus",filter =  "csv (*.csv)")
                if filepath2 is not None:
                    self.loaded_filepaths.loc[self.loaded_filepaths["Daten"][self.loaded_filepaths["Daten"] == "Mandate Vorlagen"].index, "Speicherort1"] = filepath1
                    self.loaded_filepaths.loc[self.loaded_filepaths["Daten"][self.loaded_filepaths["Daten"] == "Mandate Vorlagen"].index, "Speicherort2"] = filepath2

                    template = self.mandates.load_template(filepath1,filepath2)
                    updatetable_1_1()

        def export_csv():
            print("Export cvs")
            if self.exportwindow is None:
                #data check
                if not self.invoicesdata_loaded:
                    errorbox = QMessageBox()
                    errorbox.setText("Es wurden keine Rechungsdaten ausgewählt, wähle zuerst diese aus und versuch es nochmal.")
                    errorbox.exec_()
                    return None
                if not self.mandatesdata_loaded:
                    errorbox = QMessageBox()
                    errorbox.setText("Es wurden keine Mandatssdaten ausgewählt, wähle zuerst diese aus und versuch es nochmal.")
                    errorbox.exec_()

                    return None

                self.exportwindow = Subwindow("Exportiere .csv für SEPA")
                self.exportwindow.resize(500, 100)
                self.exportwindow.move(30, 30)
                self.exportwindow.tablegrid = QGridLayout()
                self.exportwindow.tablegrid.setColumnStretch(0,1)
                self.exportwindow.tablegrid.setColumnStretch(1,10)
                self.exportwindow.tablegrid.setColumnStretch(2,5)

                header_layout = QHBoxLayout()

                # Add header labels to the header layout
                header_label1 = QLabel("")
                header_label2 = QLabel("Name")
                header_label3 = QLabel("Betrag [€]")
                header_layout.addWidget(header_label1)
                header_layout.addWidget(header_label2)
                header_layout.addWidget(header_label3)
                header_layout.setStretch(0,1)
                header_layout.setStretch(1,10)
                header_layout.setStretch(2,5)


                self.exportwindow.list_data = []

                names = []
                amounts = []
                for idx, person in self.invoices.data["list"].iterrows():
                    name = person["Empfänger Vorame"]
                    if not pd.isna(person["Empfänger Nachname"]):
                        name += f" {person['Empfänger Nachname']}"
                    names.append(name)
                    if person["Dokumenttyp"] == "Rechnung":
                        amounts.append(-person["Rechnungsbetrag Brutto"])
                    else: amounts.append(person["Rechnungsbetrag Brutto"])

                # mandatesexist = []
                # for name in names:
                #     if (mandates.data["Zahlungspflichtiger Name"] == name).any():
                #         mandatesexist.append("x")
                #     else: mandatesexist.append("")

                for index,(name,amount) in enumerate(zip(names,amounts)):
                    index += 1
                    checkbox = QCheckBox()
                    checkbox.setChecked(True)
                    col1 = QLabel(str(name))
                    col2 = QLabel(str(amount))

                    self.exportwindow.tablegrid.addWidget(checkbox,index,0)
                    self.exportwindow.tablegrid.addWidget(col1,index,1)
                    self.exportwindow.tablegrid.addWidget(col2,index,2)

                    self.exportwindow.list_data.append(checkbox)

                # print(self.exportwindow.tablegrid.rowCount())
                # for i in range(0,self.exportwindow.tablegrid.rowCount()):
                #     self.exportwindow.tablegrid.setRowStretch(i, 0)



                def get_selected_names():
                    nr_list_widgets = len(self.exportwindow.list_data)
                    selected_names = [False] * nr_list_widgets
                    for index,checkbox in enumerate(self.exportwindow.list_data):
                        if checkbox.isChecked():
                            selected_names[index] = True

                    print(self.invoices.data["list"].loc[selected_names])
                    invoices_selected_names = self.invoices.data["list"].loc[selected_names]

                    exportingdebit,exportingtransfer, missingmandates,doublesprocess = produce_sepa_export_dfs(invoices_selected_names,self.mandates,self.mandates.data["Creditor ID"])
                    if doublesprocess["Name"]:
                        print("we merged doubes")
                        dlg = QMessageBox(self)
                        questiontext = f"Für folgende Personen gibt es sowohl Überweisungsdaten und Lastschriftdaten. Diese werden zusammengeführt:\n\n"
                        for i in range(0,len(doublesprocess["Name"])):
                            questiontext += f"{doublesprocess["Name"][i]}: Lastschrift: {doublesprocess["Debit"][i]}€, Überweisung: {doublesprocess["Transfer"][i]}€ --> {doublesprocess["Type"][i]} mit {doublesprocess["Final"][i]}€ \n"
                        dlg.setText(questiontext)
                        prompt = dlg.exec()


                    if missingmandates:
                        dlg = QMessageBox(self)
                        questiontext = f"Für folgende Personen gibt es Daten zur Lastschrift, aber keine Daten zu einem Mandat:\n\n"
                        for name in missingmandates:
                            questiontext += f"{name} \n"
                        questiontext += "\nWillst du trotzdem fortfahren? \n(Es ist eigentlich kein Problem, wenn ein Mandat fehlt, da du in Infinity noch ein Mandat hinzufügen kannst. Jedoch ist es 'Good practice' dies im Mandatenfile zu machen.)"

                        dlg.setText(questiontext)
                        dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                        prompt = dlg.exec()
                        if prompt == QMessageBox.No:
                            print("Abort")
                            return

                    print(f"df = {exportingdebit,exportingtransfer}")
                    if exportingdebit is not  None:
                        filepath1 = load_filepath(self,"Wähle Speicherort für Export für SEPA Lastschrift aus", filter="csv (*.csv)", fileex=False)
                        if filepath1 is not None:
                            if ".csv" not in filepath1:
                                filepath1 = f"{filepath1}.csv"
                            print(f"Export to: {filepath1}")
                            try:
                                exportingdebit.to_csv(filepath1, index=False,sep=";")
                            except:
                                errorbox = QMessageBox("Saving didnot work")
                                print("savning didnot work")
                        else: return
                    if exportingtransfer is not  None:
                        filepath2 = load_filepath(self,"Wähle Speicherort für Export für Überweisungen aus",
                                                  filter="csv (*.csv)", fileex=False)

                        if filepath2 is not None:
                            if ".csv" not in filepath2:
                                filepath2 = f"{filepath2}.csv"
                            print(f"Export to: {filepath2}")
                            try:
                                exportingtransfer.to_csv(filepath2, index=False,sep=";")
                            except:
                                errorbox = QMessageBox("Saving didnot work")
                                print("savning didnot work")
                        else:
                            return
                    self.exportwindow.close()
                    return selected_names


                self.exportwindow.ok_button = QPushButton("OK")
                self.exportwindow.ok_button.pressed.connect(get_selected_names)
                self.exportwindow.overallverticallayout.addLayout(header_layout)
                self.exportwindow.overallverticallayout.addLayout(self.exportwindow.tablegrid)
                # self.exportwindow.overallverticallayout.addWidget(self.exportwindow.list_widget)
                self.exportwindow.overallverticallayout.addWidget(self.exportwindow.ok_button)



                self.exportwindow.show()
            else:
                self.exportwindow.close()  # Close window.
                self.exportwindow = None  # Discard reference.

        def reload_table_view(tablenr,data):
            """

            :param tablenr: in columns on the grid "0_0","0_1","1_0"
            :param data: as a Pandas Dataframe
            :return:
            """
            tabledict = {"0_0":self.table_0_0,
                         "0_1": self.table_0_1,
                         "1_0": self.table_1_0,
                         }
            tabledict[tablenr].set_new_data(data)

        self.reload_table_view = reload_table_view

        menubardata = [["Importiere Rechnungdaten von EEG Faktura", "", import_invoice_data],
                            ["Lade Daten von SEPA Mandate", "", import_mandates],
                            ["Exportiere .csv Datei für Raiffeisen Infinty", "", export_csv]]
        return menubardata


def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys._excepthook = sys.excepthook

    def exception_hook(exctype, value, traceback):
        print("silent error")
        print(exctype, value, traceback)
        sys._excepthook(exctype, value, traceback)
        sys.exit(1)

    sys.excepthook = exception_hook
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()