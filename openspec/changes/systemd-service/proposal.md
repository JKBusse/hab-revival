# Proposal

## Why

Auf `hba1` existiert seit Juli 2024 eine `hba.service` (und `sensor.service` für die Telemetrie), beide beim Boot aktiviert, aber nicht im Repo. Die `hba.service` hat keine Neustart-Regel: Sie ist heute "failed", weil `/mnt/hba-stick` nicht eingehängt war und das Programm beim Anlegen der Logdatei abstürzte (Stand 2026-11-05). Es fehlen Neustart nach einem Absturz, ein definierter Stopp per SIGTERM und eine Wartezeit zwischen Neustarts. `gpu-required` und `fail-safe-shutdown` setzen genau das voraus.

## What Changes

- Die vorhandene **`hba.service`** wird repariert und ins Repo übernommen. Das Hauptprogramm startet beim Boot.
- Bei einem Fehler (Exit-Code ungleich 0, auch „keine GPU") startet der Dienst nach 10 s neu, **endlos** und ohne Startlimit-Sperre (Entscheidung von Jan).
- Der Dienst startet **auch ohne USB-Stick**: Fehlt die Ablage, schaltet das Programm Datei-Log und Aufnahmen ab und läuft weiter (Entscheidung von Jan).
- Ein gewollter Stopp erfolgt per SIGTERM mit Zeitlimit. Das Programm blendet dabei ab (siehe `fail-safe-shutdown`).
- Das Programm schreibt sein Log ins Journal. Die Datei-Logs unter `HBA/log/` bleiben.
- Der Dienst und seine Installation sind im Repo dokumentiert und versioniert. Das Telemetrie-Skript wird als eigener Dienst festgehalten, soweit es dafür sinnvoll ist.

## Capabilities

### New Capabilities
- `service-supervision`: Autostart, endloser Neustart mit 10 s Wartezeit und kontrollierter Stopp des Hauptprogramms durch den Dienst-Manager.

### Modified Capabilities
- `runtime-configuration`: Die Requirement „Kein dokumentierter Autostart" entfällt (die Annahme war falsch). Neu: „Ablage nicht verfügbar".
- `data-collection`: „Vorbereiteter Speicherort": fehlende Ordner führen zu WARNING statt Exception.

## Impact

- **Auf `hba1`:** die Unit `/etc/systemd/system/hba.service` wird ersetzt (alte wird gesichert), braucht sudo und ist eine dauerhafte Systemänderung. Diese Änderung wird vor dem Einrichten ausdrücklich bestätigt.
- **Repo:** Unit-Datei und Installationsanleitung unter `deploy/`.
- **Reihenfolge:** `config-file` wird vor diesem Change archiviert (gleiche Requirement betroffen).
- **Voraussetzungen:** `fail-safe-shutdown` (Exit-Codes, SIGTERM), `gpu-required` (Exit-Code „keine GPU").
- **Nicht im Umfang:** GPU-Rescan beim Boot (nach den letzten Starts wurde die GPU von selbst erkannt), Überwachung durch externe Systeme, Telemetrie-Änderungen.
