## ADDED Requirements

### Requirement: Alle Boxen werden bewertet
Das System SHALL für die Entscheidung jede Box eines Frames einzeln auf Relevanz prüfen (Breite, obere Kante, Konfidenz). Der Zeitpunkt der letzten Detektion wird aktualisiert, sobald mindestens eine Box relevant ist, unabhängig von ihrer Position in der Boxliste.

#### Scenario: Zweites Fahrzeug relevant, erstes nicht
- **WHEN** ein Frame zwei Boxen enthält und nur die zweite die Aktive Fläche erfüllt
- **THEN** wird der Zeitpunkt der letzten Detektion aktualisiert
- **AND** der Status ist im selben Frame 0

#### Scenario: Erstes Fahrzeug relevant, zweites nicht
- **WHEN** ein Frame zwei Boxen enthält und nur die erste die Aktive Fläche erfüllt
- **THEN** wird der Zeitpunkt der letzten Detektion aktualisiert

#### Scenario: Keine Box relevant
- **WHEN** ein Frame Boxen enthält, aber keine die Aktive Fläche erfüllt
- **THEN** wird der Zeitpunkt der letzten Detektion nicht aktualisiert

### Requirement: Nie weniger Abblenden als vorher
Das System SHALL für jede Frame-Folge in jedem Frame einen Status liefern, der nicht größer ist als der Status der bisherigen Logik (nur erste Box) für dieselbe Folge.

#### Scenario: Wiedergabe echter Fahrt-Logs
- **WHEN** die aufgezeichneten Frames der echten Fahrt-Logs mit der neuen Logik wiedergegeben werden
- **THEN** ist der Status in keinem Frame 1, wo die bisherige Logik 0 lieferte

#### Scenario: Zufällige Frame-Folgen
- **WHEN** beliebige Folgen von Frames mit beliebigen Boxen und Zeitpunkten mit beiden Logiken ausgewertet werden
- **THEN** ist der Status der neuen Logik nie größer als der der bisherigen

## REMOVED Requirements

### Requirement: Bewertungsgrundlage ist die erste Box (Legacy-Eigenheit)
**Reason**: Bekannter Mangel. Ist nur ein späteres Fahrzeug relevant, wird das Fernlicht trotz sichtbaren Gegenverkehrs freigegeben.
**Migration**: Ersetzt durch „Alle Boxen werden bewertet". Haltezeit, Drosselung und Aufblend-Verzögerung bleiben unverändert.
