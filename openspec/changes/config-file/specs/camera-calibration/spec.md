## ADDED Requirements

### Requirement: Kalibrier-Werkzeug
Das System SHALL ein eigenes Werkzeug `python -m hba.calibrate` bereitstellen, das ein Kamerabild (Datei oder Live-Kamera) in einem OpenCV-Fenster anzeigt. Es braucht weder GPU noch Modell noch Mikrocontroller.

#### Scenario: Start mit Testbild
- **WHEN** das Werkzeug mit `--image <datei>` startet
- **THEN** erscheint das Bild in einem Fenster
- **AND** es wird kein Serial-Port geöffnet und kein Modell geladen

#### Scenario: Start mit Live-Kamera
- **WHEN** das Werkzeug mit `--camera` startet
- **THEN** wird ein einzelnes Kamerabild aufgenommen und angezeigt

### Requirement: Darstellung im Maßstab des Filters
Das System SHALL den Erkennungsausschnitt aus dem aktuellen Konfigurationswert bilden, auf die Eingabegröße skalieren und die Aktive Fläche als Rahmen darin einzeichnen. Die Rahmen SHALL denselben Maßstab haben wie der Relevanzfilter.

#### Scenario: Standardwerte
- **WHEN** die Konfiguration die Legacy-Werte enthält
- **THEN** zeigt das Werkzeug den 960×426-Ausschnitt skaliert auf 640×640
- **AND** die Grenzen der Aktiven Fläche liegen bei Breite 500 und Zeile 160

### Requirement: Einstellen mit der Maus
Das System SHALL erlauben, den Erkennungsausschnitt im Gesamtbild und die Aktive Fläche im Ausschnitt per Maus zu verändern und die neuen Werte sofort darzustellen.

#### Scenario: Ausschnitt verschieben
- **WHEN** der Benutzer den Ausschnitt-Rahmen mit der Maus verschiebt
- **THEN** zeigt die Ausschnittsansicht sofort den neuen Bildinhalt

### Requirement: Schreiben in die Konfigurationsdatei
Das System SHALL bei Taste `s` die Werte in die Konfigurationsdatei schreiben, nachdem sie dieselbe Prüfung wie beim Programmstart bestanden haben. Nicht beteiligte Schlüssel und Kommentare der Datei bleiben erhalten. Bei Taste `q` wird ohne Schreiben beendet.

#### Scenario: Gültige Werte speichern
- **WHEN** der Benutzer `s` drückt und die Werte gültig sind
- **THEN** enthält die Datei die neuen Werte und alle übrigen Schlüssel unverändert

#### Scenario: Ungültige Werte
- **WHEN** der Benutzer `s` drückt und der Ausschnitt über das Bild hinausragt
- **THEN** wird nichts geschrieben
- **AND** die Meldung nennt den Grund
