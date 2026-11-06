# Bilder prüfen mit Label Studio

Für die 456 Bilder ohne Label (siehe `openspec/changes/dataset-cleanup`). Das Modell `medium6`
macht Vorschläge (Rahmen), **du prüfst jedes Bild** und korrigierst oder bestätigst. Label Studio
läuft lokal auf dem Mac, es verlässt kein Bild den Rechner.

Pro Bild gibt es genau drei Möglichkeiten:

| Aktion in Label Studio | Bedeutung |
|---|---|
| **Absenden (Submit)** mit Rahmen um die Fahrzeuge | geprüft, das Bild kommt mit diesem Label ins Training |
| **Absenden** ohne jeden Rahmen | geprüft, **kein Fahrzeug zu sehen**: bewusstes Negativ |
| **Skip** | verworfen, das Bild kommt nicht ins Training |

Klassen: `back` (Rücklichter, Fahrzeug fährt vor dir) und `front` (Scheinwerfer, Gegenverkehr).
Wichtig: Der Vorschlag ist **nur** ein Vorschlag. Verpasste Fahrzeuge sind der gefährliche Fall, also
bitte auch auf kleine, weit entfernte Lichter achten und fehlende Rahmen ergänzen.

## 1. Einrichten (einmalig)

```bash
python3.12 -m venv ~/label-studio-venv
~/label-studio-venv/bin/pip install label-studio
```

Starten (die Dokumentenwurzel muss den Datensatz enthalten):

```bash
export LOCAL_FILES_SERVING_ENABLED=true
export LOCAL_FILES_DOCUMENT_ROOT=/Users/janbusse/Desktop/Projekte
~/label-studio-venv/bin/label-studio start
```

Im Browser (`http://localhost:8080`) ein Konto anlegen und ein Projekt erstellen. Unter
*Settings → Labeling Interface → Code* den Inhalt von `tools/label_studio_config.xml` einfügen.

## 2. Aufgaben erzeugen und importieren

Mit Vorschlägen (nachdem die Vorlabels von `hba1` da sind):

```bash
.venv/bin/python tools/yolo_to_ls.py \
  /Users/janbusse/Desktop/Projekte/HBA4v2Dataset/train/images \
  /Users/janbusse/Desktop/Projekte/prelabel \
  tasks.json --root /Users/janbusse/Desktop/Projekte
```

Das nimmt **alle** Bilder des Ordners. Für die Prüfung gehören nur die 456 ohne Label hinein:
Das Skript wird dafür noch auf diese Auswahl eingeschränkt (siehe Aufgabe 3.3).
In Label Studio: *Import* → `tasks.json`.

## 3. Prüfen

Bild für Bild: Rahmen verschieben oder ergänzen, falsche löschen, **Submit** oder **Skip**.

## 4. Exportieren und übernehmen

*Export* → **JSON** (nicht JSON-MIN). Dann:

```bash
.venv/bin/python tools/ls_to_yolo.py export.json geprueft/
```

Das meldet `geprüft N, verworfen M, offen K`. `offen` muss 0 sein (jedes Bild braucht eine Entscheidung).
Die Übernahme ins Trainingsset und das Protokoll macht Claude danach (Aufgabe 3.5).
