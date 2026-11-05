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
Das System SHALL irrelevante Boxen in der Visualisierung gelb darstellen, relevante nach Klasse (siehe Spec `monitoring`).

#### Scenario: Irrelevante Box im Stream
- **WHEN** der Stream aktiv ist und eine Box die Aktive Fläche verfehlt
- **THEN** wird sie gelb umrandet

### Requirement: Protokollierung der Bewertung
Das System SHALL für jede Box Koordinaten, Breite, obere Kante und Bewertungsergebnis loggen.

#### Scenario: Bewertung einer Box
- **WHEN** eine Box bewertet wird
- **THEN** enthält das Log `Len`, `Hei` und `In active area`
