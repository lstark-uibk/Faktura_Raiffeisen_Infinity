Kleines Programm um exportierte EEG Faktura Daten zum Import auf Raiffeisen Infintiy vorzubreiten.

Getestet auf Python 3.12
Braucht: pandas, PyQt5

Workflow:
1. Exportiere die Rechnungsdaten von EEG Faktura (dies sollte dann so wie die Beispieldatei in diesem Repo ausschauen).
2. Erstelle eine Datei mit all den Daten für SEPA Mandate (wie die Beispieldatei in diesem Repo)
3. Importiere beide dateien in Faktura_Raiffeisen_Infinity Programm
4. Exportiere die Rechnungsdaten für Raiffeisen Infinity
5. Importiere diese Datei in  Raiffeisen Infinity unter Aufträge -> Import
