# Änderungsprotokoll Trainingsdatensatz

Jede Änderung am Trainingsset `train` mit Datei, Aktion und Grund. Quelle: `tools/cleanup_dataset.py` und die Bildprüfung. `valid` und `test` werden nie verändert (Prüfsummen: `HBA4v2.valid_test.sha256`).

| Datum | Datei | Aktion | Grund |
|---|---|---|---|
| 2026-11-06 | `train/labels/16983622104879258.txt` | entfernt | Label ohne Bild |
| 2026-11-06 | `train/labels/16983622108154483.txt` | entfernt | Label ohne Bild |
| 2026-11-06 | `train/labels/16983622109797027.txt` | entfernt | Label ohne Bild |
| 2026-11-06 | `train/*/NOR16952457630867074_png.rf.3a0a82e2e936cc27c950b3aa2d4b7986.* -> train/*/OFF_NOR16952457630867074_png.rf.3a0a82e2e936cc27c950b3aa2d4b7986.*` | umbenannt | leeres Label, Bild zeigt kein Fahrzeug: bewusstes Negativ |
| 2026-11-06 | `train/*/NOR16952457633193877_png.rf.437e93b192b9d62f59a08534ccbc30b5.* -> train/*/OFF_NOR16952457633193877_png.rf.437e93b192b9d62f59a08534ccbc30b5.*` | umbenannt | leeres Label, Bild zeigt kein Fahrzeug: bewusstes Negativ |
| 2026-11-06 | `train/*/NOR16952464712820249_png.rf.caaebac93e128c166b5fd4e9944e81e2.* -> train/*/OFF_NOR16952464712820249_png.rf.caaebac93e128c166b5fd4e9944e81e2.*` | umbenannt | leeres Label, Bild zeigt kein Fahrzeug: bewusstes Negativ |
| 2026-11-06 | `train/*/NOR16952464714965043_png.rf.9fa711d4fea92f4f2c0f065b288d2122.* -> train/*/OFF_NOR16952464714965043_png.rf.9fa711d4fea92f4f2c0f065b288d2122.*` | umbenannt | leeres Label, Bild zeigt kein Fahrzeug: bewusstes Negativ |
| 2026-11-06 | `train/*/NOR16952468902110796_png.rf.37ea49b2f75cdf1c1b0d32fd7fb5b7b7.* -> train/*/OFF_NOR16952468902110796_png.rf.37ea49b2f75cdf1c1b0d32fd7fb5b7b7.*` | umbenannt | leeres Label, Bild zeigt kein Fahrzeug: bewusstes Negativ |
| 2026-11-06 | `train/labels/NOR16952471422706_png.rf.16d2a9e803e53b1ed5fb2cdebd5a8add.txt` | entfernt | Label ohne Bild |
| 2026-11-06 | `train/*/NOR16952472223773699_png.rf.dc6cbfed6fbbc013e50fac8351576fb5.* -> train/*/OFF_NOR16952472223773699_png.rf.dc6cbfed6fbbc013e50fac8351576fb5.*` | umbenannt | leeres Label, Bild zeigt kein Fahrzeug: bewusstes Negativ |
| 2026-11-06 | `train/*/NOR1695247309104704_png.rf.65303a5ce138bc949ea2af008487def2.* -> train/*/OFF_NOR1695247309104704_png.rf.65303a5ce138bc949ea2af008487def2.*` | umbenannt | leeres Label, Bild zeigt kein Fahrzeug: bewusstes Negativ |
| 2026-11-06 | `train/*/NOR169524783273708_png.rf.b35457851245e63d5ed608371bf02597.* -> train/*/OFF_NOR169524783273708_png.rf.b35457851245e63d5ed608371bf02597.*` | umbenannt | leeres Label, Bild zeigt kein Fahrzeug: bewusstes Negativ |
