# Design

## Context

Das Trainingsset `HBA4v2Dataset/train` enthält 456 Roh-Captures ohne Label-Datei, 4 verwaiste Labels und uneinheitliche Klassenschreibweise. 495 leere `OFF…`-Labels sind gewollte Negative. `medium6` erreicht Precision 0,85, Recall 0,87, mAP50 0,88. Jan hat wenig Erfahrung mit dem Training von ML-Modellen, deshalb legt dieses Design die technischen Details fest und lässt Jan nur Aufwand und Freigaben entscheiden.

Die GPU auf `hba1` ist unter hoher Last instabil (Xid 79 bei etwa 117 W, stabil bei etwa 65 W über 10 Minuten). Training darf deshalb nur mit Schutzmaßnahmen laufen.

## Goals / Non-Goals

**Goals:**
- Ein Trainingsset, bei dem jede Abweichung maschinell erkennbar ist.
- Ein neues Modell nur, wenn es nachweislich nicht schlechter ist als `medium6`.

**Non-Goals:**
- Keine anderen Architekturen, keine neuen Klassen, keine zusätzliche Datensammlung.

## Decisions

### 1. Vorlabeln durch `medium6`, Prüfung durch Jan (Entscheidung A)

`medium6` erzeugt auf `hba1` Vorlabels für die 456 Bilder (Schwelle 0,25, damit auch unsichere Treffer als Vorschlag erscheinen). Die Ausgabe landet in `prelabel/`, außerhalb des Trainingssets. Jan prüft jedes Bild und korrigiert fehlende oder falsche Rahmen. Nur geprüfte Bilder wandern nach `train/`.

*Risiko:* Das Modell würde sonst mit seinen eigenen Fehlern trainiert, vor allem mit verpassten Fahrzeugen. Die menschliche Prüfung ist deshalb Pflicht, nicht Option. Ein Bild ohne Prüfung wird verworfen, nie als Negativ behalten.

*Alternativen:* Alles von Hand (hoher Aufwand), alle 456 entfernen (verliert Material).

### 2. Label Studio lokal (Entscheidung von Jan)

Auf dem Mac ist kein Docker vorhanden, CVAT entfällt. Label Studio läuft per `pip` in einer eigenen virtuellen Umgebung (Python 3.11 oder 3.12, weil 3.13 für Label Studio nicht gesichert ist). Zwei kleine Skripte wandeln YOLO-Vorlabels in das Label-Studio-Format und zurück: `yolo_to_ls.py` und `ls_to_yolo.py`. Beide haben Rundreise-Tests (YOLO → LS → YOLO ergibt dieselben Zeilen bis auf Rundung).

### 3. Prüfroutine als Torwächter

`tools/check_dataset.py` prüft die Regeln aus der Spec: Label für jedes Bild, leer nur bei `OFF`, keine Verwaisten, Klassen, Wertebereiche. Sie läuft vor jedem Training und liefert Exit-Code ungleich 0 bei Verstößen. Der Trainingsstart ruft sie auf.

### 4. Änderungsprotokoll und Prüfsummen

`DATASET_CHANGES.md` hält jede Änderung fest. Zusätzlich speichert `tools/check_dataset.py --checksums` Prüfsummen von `valid` und `test`, die nach der Bereinigung gegengeprüft werden. So lässt sich belegen, dass der Vergleich mit `medium6` fair ist.

### 5. Nur `train` wächst

Die 456 Bilder und alle neuen Labels gehören nach `train`. `valid` und `test` bleiben unverändert. Ein Modell, das auf besser gelabelten Daten trainiert wurde, wird auf denselben Prüfbildern wie `medium6` gemessen.

### 6. Training mit Einstellungen von `medium6`

Architektur, Bildgröße und Hyperparameter kommen aus `medium6/args.yaml` auf `hba1`. Abweichungen werden begründet im Protokoll festgehalten. Der Lauf nutzt `save_period=1` (Checkpoint je Epoche) und `resume`. Er läuft detached auf `hba1`, die Logs werden gelesen.

### 7. GPU-Freigabe vor dem Training

30 Minuten echte Inferenz mit `medium6` bei 65 W (Leistungsgrenze per `nvidia-smi -pl 65`, benötigt sudo und wird vorher bestätigt), ohne Xid-Fehler im Kernel-Log und ohne Abbruch. Danach eine Probeepoche. Erst dann der volle Lauf. Das deckt die offene Frage ab, ob die GPU unter echter Trainingslast hält.

### 8. Strenge Abnahme

Neues Modell ersetzt `medium6` nur, wenn Recall gesamt, Recall `front`, mAP50 und Frame-Zeit nicht schlechter sind (Frame-Zeit Median höchstens 0,15 s). `front` ist der Gegenverkehr, dessen Verpassen blendet. Der Vergleich verwendet denselben `valid`- und `test`-Satz. Ein verfehltes Kriterium bedeutet: kein Austausch, Befund dokumentieren.

*Folge:* Ein Training kann ohne Austausch enden. Das ist akzeptiert, weil `medium6` bewährt ist.

### 9. Austausch ist eine Konfigurationsänderung

Das neue Modell liegt unter eigenem Namen neben `medium6`. Umgestellt wird der Modellpfad in der Konfiguration (`config-file`). Rückfall ist derselbe Weg zurück.

## Risks / Trade-offs

- **Jan prüft nachlässig oder ermüdet bei 456 Bildern** → Stichprobenkontrolle: ich ziehe 20 geprüfte Bilder zufällig und zeige sie zur Gegenprüfung. Fehler im Set werden im Protokoll nachvollziehbar.
- **GPU fällt unter Trainingslast aus** → 65 W, Checkpoints, `resume`, vorgeschalteter Dauertest.
- **Kein Austausch trotz Mühe** → Akzeptiert (strenge Abnahme).
- **Label Studio unter Python 3.13 nicht lauffähig** → eigene venv mit 3.11 oder 3.12, sonst Wechsel auf labelImg.
- **Vorlabels verleiten zum Durchwinken** → Pflicht zur Entscheidung je Bild, Stichprobenkontrolle.

## Migration Plan

1. Prüfroutine schreiben, Ist-Zustand messen und Bereinigung der Verwaisten und Schreibweise durchführen.
2. Vorlabels auf `hba1` erzeugen, nach Mac holen, Label Studio einrichten, Jan prüft.
3. Ergebnisse ins Set übernehmen, Protokoll schreiben, Prüfsummen vergleichen.
4. GPU-Freigabe, dann Training auf `hba1`.
5. Auswertung gegen `medium6`, Entscheidung über den Austausch.

Rollback: Originaldatensatz bleibt als unveränderte Kopie liegen. `medium6` bleibt Standard, bis ein Modell die Abnahme besteht.

## Open Questions

- Einstellungen aus `medium6/args.yaml` (Epochen, Batch, Augmentierung): erst nach dem Lesen auf `hba1` bekannt.
- Wie viele Epochen und wie lange ein Lauf auf der P106-100 dauert, ist erst nach der Probeepoche abschätzbar.

## Messwerte `hba1` (2026-11-08)

- 30 min Inferenz mit `medium6` bei 65 W: 22.333 Frames, Median 0,078 s, kein Xid. Das Limit ist kein harter Deckel: 60 von 537 Messpunkten lagen darüber (Spitze 88 W), Temperatur höchstens 50 °C.
- Probeepoche (`medium6/best.pt` als Start, 3.274 Trainingsbilder, `imgsz=640`, `workers=2`): **Batch 16 bricht mit CUDA-Speichermangel ab** (6 GB), **Batch 8 läuft**: 0,130 h (7,8 min) je Epoche inklusive Validierung, Spitze 85 W, höchstens 52 °C, 4,3 GB Speicher, kein Xid. Ein Training braucht daher Batch 8 (nicht `batch=-1` wie bei `medium6`) und `workers` höchstens 2 (4 Kerne, 3,8 GB RAM).
