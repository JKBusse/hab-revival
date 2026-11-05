# relevance-filter Specification

## Purpose
Beschreibt, wann eine erkannte Box im Legacy-System als „sinnvolle" Detektion zählt („Active Area"), damit Störobjekte das Fernlicht nicht grundlos abblenden.

## Requirements

### Requirement: Aktive Fläche
Das System SHALL eine Box als relevant werten, wenn ihre Breite kleiner als 500 Pixel ist **und** ihre obere Kante (y1) unterhalb von Pixelzeile 160 liegt (y1 > 160). Alle Werte beziehen sich auf das 640×640-Eingabebild.

#### Scenario: Normales Fahrzeug
- **WHEN** eine Box 80 Pixel breit ist und ihre obere Kante bei y=250 liegt
- **THEN** ist sie relevant

#### Scenario: Zu breite Box
- **WHEN** eine Box 520 Pixel breit ist
- **THEN** ist sie nicht relevant

#### Scenario: Box zu weit oben im Bild
- **WHEN** eine Box 80 Pixel breit ist und ihre obere Kante bei y=100 liegt
- **THEN** ist sie nicht relevant

### Requirement: Irrelevante Boxen werden markiert
Das System SHALL Boxen, die schmaler als 500 Pixel sind, aber mit ihrer oberen Kante nicht unter Zeile 160 liegen, in der Visualisierung gelb darstellen. Zu breite Boxen werden nach Klasse gefärbt (siehe Spec `monitoring`). Für die Entscheidung sind beide Fälle gleichermaßen nicht relevant.

#### Scenario: Irrelevante Box im Stream
- **WHEN** der Stream aktiv ist und eine schmale Box zu weit oben liegt
- **THEN** wird sie gelb umrandet

### Requirement: Protokollierung der Bewertung
Das System SHALL für jede Box Koordinaten, Breite, obere Kante und Bewertungsergebnis loggen. Das Ergebnis ist `True` (relevant), `None` (schmal, aber zu weit oben) oder `False` (zu breit).

#### Scenario: Bewertung einer Box
- **WHEN** eine Box bewertet wird
- **THEN** enthält das Log `Len`, `Hei` und `In active area`

#### Scenario: Box zu weit oben
- **WHEN** eine schmale Box mit oberer Kante bei y=100 bewertet wird
- **THEN** steht im Log `In active area 0 : None`
