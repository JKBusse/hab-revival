## MODIFIED Requirements

### Requirement: Aktive Fläche
Das System SHALL eine Box als relevant werten, wenn ihre Breite kleiner als `max_width` ist **und** ihre obere Kante (y1) größer als `min_top` ist. Standard sind 500 und 160. Alle Werte beziehen sich auf das 640×640-Eingabebild.

#### Scenario: Normales Fahrzeug
- **WHEN** eine Box 80 Pixel breit ist und ihre obere Kante bei y=250 liegt
- **THEN** ist sie relevant

#### Scenario: Zu breite Box
- **WHEN** eine Box 520 Pixel breit ist und `max_width` 500 beträgt
- **THEN** ist sie nicht relevant

#### Scenario: Box zu weit oben im Bild
- **WHEN** eine Box 80 Pixel breit ist, ihre obere Kante bei y=100 liegt und `min_top` 160 beträgt
- **THEN** ist sie nicht relevant

#### Scenario: Geänderte Schwelle
- **WHEN** `min_top` auf 100 gesetzt ist und die obere Kante bei y=120 liegt
- **THEN** ist die Box relevant
