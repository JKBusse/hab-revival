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
| 2026-11-08 | `train/*/16982771869168143.* -> train/*/OFF_16982771869168143.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982771877100153.* -> train/*/OFF_16982771877100153.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982771888607275.* -> train/*/OFF_16982771888607275.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982771890397909.* -> train/*/OFF_16982771890397909.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982772190318732.* -> train/*/OFF_16982772190318732.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982772191991265.* -> train/*/OFF_16982772191991265.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982772498612845.* -> train/*/OFF_16982772498612845.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982772500315814.* -> train/*/OFF_16982772500315814.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982772503655508.* -> train/*/OFF_16982772503655508.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982772803700075.* -> train/*/OFF_16982772803700075.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/169827733185796.* -> train/*/OFF_169827733185796.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698277332025406.* -> train/*/OFF_1698277332025406.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982773613830936.* -> train/*/OFF_16982773613830936.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982773620377426.* -> train/*/OFF_16982773620377426.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698277362207274.* -> train/*/OFF_1698277362207274.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982773623681107.* -> train/*/OFF_16982773623681107.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698277444357018.* -> train/*/OFF_1698277444357018.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982775613309343.* -> train/*/OFF_16982775613309343.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982775614836686.* -> train/*/OFF_16982775614836686.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698277562322538.* -> train/*/OFF_1698277562322538.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982775624718893.* -> train/*/OFF_16982775624718893.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982775860565858.* -> train/*/OFF_16982775860565858.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698277586223996.* -> train/*/OFF_1698277586223996.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982775863871684.* -> train/*/OFF_16982775863871684.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982775877079701.* -> train/*/OFF_16982775877079701.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982775878811378.* -> train/*/OFF_16982775878811378.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982776131092663.* -> train/*/OFF_16982776131092663.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698277613276086.* -> train/*/OFF_1698277613276086.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698277613437613.* -> train/*/OFF_1698277613437613.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982776136054206.* -> train/*/OFF_16982776136054206.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982776419769108.* -> train/*/OFF_16982776419769108.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982776719930685.* -> train/*/OFF_16982776719930685.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982777453032632.* -> train/*/OFF_16982777453032632.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982777487519085.* -> train/*/OFF_16982777487519085.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982777489193108.* -> train/*/OFF_16982777489193108.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982778358289871.* -> train/*/OFF_16982778358289871.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982778371359007.* -> train/*/OFF_16982778371359007.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698277837334131.* -> train/*/OFF_1698277837334131.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982778374879146.* -> train/*/OFF_16982778374879146.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698277837634943.* -> train/*/OFF_1698277837634943.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982778377884982.* -> train/*/OFF_16982778377884982.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982778456636825.* -> train/*/OFF_16982778456636825.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982778687915149.* -> train/*/OFF_16982778687915149.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982778689547791.* -> train/*/OFF_16982778689547791.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/images/1698277952098308.png` | entfernt | Bildprüfung: verworfen (Skip) |
| 2026-11-08 | `train/images/16982779522587225.png` | entfernt | Bildprüfung: verworfen (Skip) |
| 2026-11-08 | `train/images/16982779836055932.png` | entfernt | Bildprüfung: verworfen (Skip) |
| 2026-11-08 | `train/*/16982780167122507.* -> train/*/OFF_16982780167122507.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982784151962738.* -> train/*/OFF_16982784151962738.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982784153709376.* -> train/*/OFF_16982784153709376.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982785808584373.* -> train/*/OFF_16982785808584373.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698278581019937.* -> train/*/OFF_1698278581019937.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982785911651251.* -> train/*/OFF_16982785911651251.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982786323262856.* -> train/*/OFF_16982786323262856.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982786324919617.* -> train/*/OFF_16982786324919617.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982786331469302.* -> train/*/OFF_16982786331469302.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982786336475267.* -> train/*/OFF_16982786336475267.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982786712020466.* -> train/*/OFF_16982786712020466.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982786759448652.* -> train/*/OFF_16982786759448652.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698278676115023.* -> train/*/OFF_1698278676115023.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982786810340657.* -> train/*/OFF_16982786810340657.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982786836543171.* -> train/*/OFF_16982786836543171.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982786867713706.* -> train/*/OFF_16982786867713706.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698278687262941.* -> train/*/OFF_1698278687262941.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982786893969996.* -> train/*/OFF_16982786893969996.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982786925106947.* -> train/*/OFF_16982786925106947.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982786931719697.* -> train/*/OFF_16982786931719697.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982786941569147.* -> train/*/OFF_16982786941569147.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982786979588008.* -> train/*/OFF_16982786979588008.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982787025224793.* -> train/*/OFF_16982787025224793.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/labels/16982787026882417.txt` | gelabelt | Bildprüfung: geprüft, 1 Rahmen |
| 2026-11-08 | `train/*/16982787028730338.* -> train/*/OFF_16982787028730338.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982787030356858.* -> train/*/OFF_16982787030356858.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/images/1698278765485567.png` | entfernt | Bildprüfung: verworfen (Skip) |
| 2026-11-08 | `train/images/1698278765681119.png` | entfernt | Bildprüfung: verworfen (Skip) |
| 2026-11-08 | `train/*/16982790619947278.* -> train/*/OFF_16982790619947278.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982790621572788.* -> train/*/OFF_16982790621572788.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982790623229156.* -> train/*/OFF_16982790623229156.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982790624856324.* -> train/*/OFF_16982790624856324.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982790626519291.* -> train/*/OFF_16982790626519291.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982790629812965.* -> train/*/OFF_16982790629812965.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982790769209394.* -> train/*/OFF_16982790769209394.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982790770884285.* -> train/*/OFF_16982790770884285.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982791626970854.* -> train/*/OFF_16982791626970854.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982791656533403.* -> train/*/OFF_16982791656533403.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982791658186455.* -> train/*/OFF_16982791658186455.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698279257802808.* -> train/*/OFF_1698279257802808.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982793060163572.* -> train/*/OFF_16982793060163572.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982793061832402.* -> train/*/OFF_16982793061832402.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982793081499536.* -> train/*/OFF_16982793081499536.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982793083150413.* -> train/*/OFF_16982793083150413.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982793086511252.* -> train/*/OFF_16982793086511252.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698279309298572.* -> train/*/OFF_1698279309298572.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982793096280372.* -> train/*/OFF_16982793096280372.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982793185025272.* -> train/*/OFF_16982793185025272.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982793186631093.* -> train/*/OFF_16982793186631093.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698279324712555.* -> train/*/OFF_1698279324712555.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982793297967157.* -> train/*/OFF_16982793297967157.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982793299611723.* -> train/*/OFF_16982793299611723.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698279330123968.* -> train/*/OFF_1698279330123968.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982793314589264.* -> train/*/OFF_16982793314589264.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982793352096417.* -> train/*/OFF_16982793352096417.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982793412777503.* -> train/*/OFF_16982793412777503.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982793435738025.* -> train/*/OFF_16982793435738025.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982793491582417.* -> train/*/OFF_16982793491582417.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982793493150132.* -> train/*/OFF_16982793493150132.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982793496425486.* -> train/*/OFF_16982793496425486.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698279349969589.* -> train/*/OFF_1698279349969589.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982793529209032.* -> train/*/OFF_16982793529209032.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982793724581647.* -> train/*/OFF_16982793724581647.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698279372622048.* -> train/*/OFF_1698279372622048.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698279392935564.* -> train/*/OFF_1698279392935564.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982793930984704.* -> train/*/OFF_16982793930984704.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982793932636838.* -> train/*/OFF_16982793932636838.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982793934271011.* -> train/*/OFF_16982793934271011.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982794027744668.* -> train/*/OFF_16982794027744668.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982794029401157.* -> train/*/OFF_16982794029401157.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982794031346307.* -> train/*/OFF_16982794031346307.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982794032985826.* -> train/*/OFF_16982794032985826.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982794883799908.* -> train/*/OFF_16982794883799908.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982794885440242.* -> train/*/OFF_16982794885440242.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698279491989256.* -> train/*/OFF_1698279491989256.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698279517573419.* -> train/*/OFF_1698279517573419.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982795180644898.* -> train/*/OFF_16982795180644898.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982795182298894.* -> train/*/OFF_16982795182298894.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982795183937464.* -> train/*/OFF_16982795183937464.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982795185583546.* -> train/*/OFF_16982795185583546.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698279518720848.* -> train/*/OFF_1698279518720848.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982795611930208.* -> train/*/OFF_16982795611930208.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982795697213917.* -> train/*/OFF_16982795697213917.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982795699096823.* -> train/*/OFF_16982795699096823.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698279589563291.* -> train/*/OFF_1698279589563291.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982796400747647.* -> train/*/OFF_16982796400747647.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982796613963737.* -> train/*/OFF_16982796613963737.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982797060021248.* -> train/*/OFF_16982797060021248.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698279706495628.* -> train/*/OFF_1698279706495628.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982797066583974.* -> train/*/OFF_16982797066583974.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698279706986305.* -> train/*/OFF_1698279706986305.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982797071514099.* -> train/*/OFF_16982797071514099.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982797073141809.* -> train/*/OFF_16982797073141809.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698279745877125.* -> train/*/OFF_1698279745877125.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982797748802965.* -> train/*/OFF_16982797748802965.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982797780076244.* -> train/*/OFF_16982797780076244.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/images/16982798206340883.png` | entfernt | Bildprüfung: verworfen (Skip) |
| 2026-11-08 | `train/*/16982798237535083.* -> train/*/OFF_16982798237535083.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698279823914929.* -> train/*/OFF_1698279823914929.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982798265372217.* -> train/*/OFF_16982798265372217.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982798608133876.* -> train/*/OFF_16982798608133876.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982798886935463.* -> train/*/OFF_16982798886935463.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982798891855028.* -> train/*/OFF_16982798891855028.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982798893503656.* -> train/*/OFF_16982798893503656.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982799031285067.* -> train/*/OFF_16982799031285067.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982799065705507.* -> train/*/OFF_16982799065705507.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982799067371156.* -> train/*/OFF_16982799067371156.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982799195283098.* -> train/*/OFF_16982799195283098.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982799347822728.* -> train/*/OFF_16982799347822728.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982799349438572.* -> train/*/OFF_16982799349438572.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982799351096013.* -> train/*/OFF_16982799351096013.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982799370815678.* -> train/*/OFF_16982799370815678.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982799372426238.* -> train/*/OFF_16982799372426238.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698279939863742.* -> train/*/OFF_1698279939863742.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982799400480185.* -> train/*/OFF_16982799400480185.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982799495380752.* -> train/*/OFF_16982799495380752.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698279949704028.* -> train/*/OFF_1698279949704028.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982799498657322.* -> train/*/OFF_16982799498657322.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982799500319219.* -> train/*/OFF_16982799500319219.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698279950194824.* -> train/*/OFF_1698279950194824.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982799503622596.* -> train/*/OFF_16982799503622596.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982799506905353.* -> train/*/OFF_16982799506905353.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698279950852643.* -> train/*/OFF_1698279950852643.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982799511815903.* -> train/*/OFF_16982799511815903.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982799513467872.* -> train/*/OFF_16982799513467872.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982799515097396.* -> train/*/OFF_16982799515097396.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982799516767273.* -> train/*/OFF_16982799516767273.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982799518387747.* -> train/*/OFF_16982799518387747.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982799520036285.* -> train/*/OFF_16982799520036285.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982799521660316.* -> train/*/OFF_16982799521660316.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982799523305342.* -> train/*/OFF_16982799523305342.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982799524933493.* -> train/*/OFF_16982799524933493.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698279952659042.* -> train/*/OFF_1698279952659042.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982799528210623.* -> train/*/OFF_16982799528210623.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982799529856625.* -> train/*/OFF_16982799529856625.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982799549522188.* -> train/*/OFF_16982799549522188.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16982799551148245.* -> train/*/OFF_16982799551148245.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983607646060052.* -> train/*/OFF_16983607646060052.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983607651095572.* -> train/*/OFF_16983607651095572.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983607652615364.* -> train/*/OFF_16983607652615364.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983607657563918.* -> train/*/OFF_16983607657563918.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983607670792248.* -> train/*/OFF_16983607670792248.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983607675763843.* -> train/*/OFF_16983607675763843.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983607702149513.* -> train/*/OFF_16983607702149513.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/169836077069206.* -> train/*/OFF_169836077069206.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983607708466804.* -> train/*/OFF_16983607708466804.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983607710063179.* -> train/*/OFF_16983607710063179.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983607718271914.* -> train/*/OFF_16983607718271914.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983607719953253.* -> train/*/OFF_16983607719953253.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983607729779804.* -> train/*/OFF_16983607729779804.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983607731453383.* -> train/*/OFF_16983607731453383.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983607733062215.* -> train/*/OFF_16983607733062215.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983607734733121.* -> train/*/OFF_16983607734733121.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698360773658167.* -> train/*/OFF_1698360773658167.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983607738265202.* -> train/*/OFF_16983607738265202.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983607739862552.* -> train/*/OFF_16983607739862552.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983607741562798.* -> train/*/OFF_16983607741562798.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983607743001785.* -> train/*/OFF_16983607743001785.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698360774459509.* -> train/*/OFF_1698360774459509.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983607785585344.* -> train/*/OFF_16983607785585344.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/169836077872346.* -> train/*/OFF_169836077872346.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983607944629786.* -> train/*/OFF_16983607944629786.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983607990550482.* -> train/*/OFF_16983607990550482.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983609401442065.* -> train/*/OFF_16983609401442065.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983609404468536.* -> train/*/OFF_16983609404468536.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983609427403493.* -> train/*/OFF_16983609427403493.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983609429077616.* -> train/*/OFF_16983609429077616.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983609430689735.* -> train/*/OFF_16983609430689735.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983609432357633.* -> train/*/OFF_16983609432357633.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983609470155818.* -> train/*/OFF_16983609470155818.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983609471839008.* -> train/*/OFF_16983609471839008.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983609473428257.* -> train/*/OFF_16983609473428257.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983609484941342.* -> train/*/OFF_16983609484941342.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983609496420069.* -> train/*/OFF_16983609496420069.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983609750594184.* -> train/*/OFF_16983609750594184.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983609752307801.* -> train/*/OFF_16983609752307801.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983609754088395.* -> train/*/OFF_16983609754088395.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983609757176135.* -> train/*/OFF_16983609757176135.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/images/16983609780485742.png` | entfernt | Bildprüfung: verworfen (Skip) |
| 2026-11-08 | `train/images/16983609783705857.png` | entfernt | Bildprüfung: verworfen (Skip) |
| 2026-11-08 | `train/images/1698360978514764.png` | entfernt | Bildprüfung: verworfen (Skip) |
| 2026-11-08 | `train/images/16983609786633132.png` | entfernt | Bildprüfung: verworfen (Skip) |
| 2026-11-08 | `train/images/1698360979207259.png` | entfernt | Bildprüfung: verworfen (Skip) |
| 2026-11-08 | `train/images/16983609793657675.png` | entfernt | Bildprüfung: verworfen (Skip) |
| 2026-11-08 | `train/*/16983609799969702.* -> train/*/OFF_16983609799969702.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/labels/16983609804807873.txt` | gelabelt | Bildprüfung: geprüft, 1 Rahmen |
| 2026-11-08 | `train/images/16983609821586792.png` | entfernt | Bildprüfung: verworfen (Skip) |
| 2026-11-08 | `train/images/16983609832968462.png` | entfernt | Bildprüfung: verworfen (Skip) |
| 2026-11-08 | `train/labels/16983609834268355.txt` | gelabelt | Bildprüfung: geprüft, 1 Rahmen |
| 2026-11-08 | `train/labels/16983609835999143.txt` | gelabelt | Bildprüfung: geprüft, 1 Rahmen |
| 2026-11-08 | `train/labels/16983609837689412.txt` | gelabelt | Bildprüfung: geprüft, 1 Rahmen |
| 2026-11-08 | `train/*/16983610037607381.* -> train/*/OFF_16983610037607381.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698361008202407.* -> train/*/OFF_1698361008202407.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983610092023952.* -> train/*/OFF_16983610092023952.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698361009343795.* -> train/*/OFF_1698361009343795.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983610257706652.* -> train/*/OFF_16983610257706652.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983610277092533.* -> train/*/OFF_16983610277092533.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983610280382364.* -> train/*/OFF_16983610280382364.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983610287027488.* -> train/*/OFF_16983610287027488.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983610288621504.* -> train/*/OFF_16983610288621504.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698361029022837.* -> train/*/OFF_1698361029022837.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983610291908052.* -> train/*/OFF_16983610291908052.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983610319761133.* -> train/*/OFF_16983610319761133.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983610321376026.* -> train/*/OFF_16983610321376026.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983614448376634.* -> train/*/OFF_16983614448376634.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983614453306117.* -> train/*/OFF_16983614453306117.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698361445498956.* -> train/*/OFF_1698361445498956.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983614456562233.* -> train/*/OFF_16983614456562233.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983614458260076.* -> train/*/OFF_16983614458260076.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983614459985318.* -> train/*/OFF_16983614459985318.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983614615562146.* -> train/*/OFF_16983614615562146.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/169836146286736.* -> train/*/OFF_169836146286736.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983614737059462.* -> train/*/OFF_16983614737059462.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983615634142392.* -> train/*/OFF_16983615634142392.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698361563745859.* -> train/*/OFF_1698361563745859.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698361563907559.* -> train/*/OFF_1698361563907559.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983615640745912.* -> train/*/OFF_16983615640745912.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983615642571425.* -> train/*/OFF_16983615642571425.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698361564427502.* -> train/*/OFF_1698361564427502.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698361564570684.* -> train/*/OFF_1698361564570684.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698361564732923.* -> train/*/OFF_1698361564732923.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983615648917656.* -> train/*/OFF_16983615648917656.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698361598842299.* -> train/*/OFF_1698361598842299.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698361949038196.* -> train/*/OFF_1698361949038196.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983619847931547.* -> train/*/OFF_16983619847931547.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698361990697838.* -> train/*/OFF_1698361990697838.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983620039835718.* -> train/*/OFF_16983620039835718.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698362051061204.* -> train/*/OFF_1698362051061204.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698362090265963.* -> train/*/OFF_1698362090265963.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983620910890985.* -> train/*/OFF_16983620910890985.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698362091249459.* -> train/*/OFF_1698362091249459.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698362095840604.* -> train/*/OFF_1698362095840604.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983620960078037.* -> train/*/OFF_16983620960078037.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698362096990117.* -> train/*/OFF_1698362096990117.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983620971504593.* -> train/*/OFF_16983620971504593.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983620973189147.* -> train/*/OFF_16983620973189147.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698362097478713.* -> train/*/OFF_1698362097478713.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983620976430132.* -> train/*/OFF_16983620976430132.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983620978106058.* -> train/*/OFF_16983620978106058.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983620979727762.* -> train/*/OFF_16983620979727762.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/169836209813899.* -> train/*/OFF_169836209813899.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983620983003016.* -> train/*/OFF_16983620983003016.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983622613419964.* -> train/*/OFF_16983622613419964.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983624274996307.* -> train/*/OFF_16983624274996307.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983625239456992.* -> train/*/OFF_16983625239456992.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983625265643146.* -> train/*/OFF_16983625265643146.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983625267315705.* -> train/*/OFF_16983625267315705.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698362526894413.* -> train/*/OFF_1698362526894413.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983625626541507.* -> train/*/OFF_16983625626541507.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983625628212428.* -> train/*/OFF_16983625628212428.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983625629825065.* -> train/*/OFF_16983625629825065.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983625631481311.* -> train/*/OFF_16983625631481311.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983625633157349.* -> train/*/OFF_16983625633157349.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983625641365013.* -> train/*/OFF_16983625641365013.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983627425923417.* -> train/*/OFF_16983627425923417.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983627473467655.* -> train/*/OFF_16983627473467655.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983627481704378.* -> train/*/OFF_16983627481704378.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983627483313308.* -> train/*/OFF_16983627483313308.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983627660471807.* -> train/*/OFF_16983627660471807.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983627662076964.* -> train/*/OFF_16983627662076964.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698362766376933.* -> train/*/OFF_1698362766376933.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983627665361092.* -> train/*/OFF_16983627665361092.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983628226652856.* -> train/*/OFF_16983628226652856.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983628228302672.* -> train/*/OFF_16983628228302672.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983628854207394.* -> train/*/OFF_16983628854207394.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983628855004067.* -> train/*/OFF_16983628855004067.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983628855787923.* -> train/*/OFF_16983628855787923.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983628856565616.* -> train/*/OFF_16983628856565616.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983628857344422.* -> train/*/OFF_16983628857344422.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698362885812749.* -> train/*/OFF_1698362885812749.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983628859423163.* -> train/*/OFF_16983628859423163.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698362918057026.* -> train/*/OFF_1698362918057026.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983629181424308.* -> train/*/OFF_16983629181424308.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983629182201235.* -> train/*/OFF_16983629182201235.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698362918300149.* -> train/*/OFF_1698362918300149.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983629183782496.* -> train/*/OFF_16983629183782496.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/169836297156832.* -> train/*/OFF_169836297156832.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983629717302563.* -> train/*/OFF_16983629717302563.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983629718961182.* -> train/*/OFF_16983629718961182.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698363265008762.* -> train/*/OFF_1698363265008762.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698363265337365.* -> train/*/OFF_1698363265337365.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983632656661675.* -> train/*/OFF_16983632656661675.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983632733738635.* -> train/*/OFF_16983632733738635.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983632756702662.* -> train/*/OFF_16983632756702662.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983632973224277.* -> train/*/OFF_16983632973224277.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983632974846096.* -> train/*/OFF_16983632974846096.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983632976510105.* -> train/*/OFF_16983632976510105.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983632979782693.* -> train/*/OFF_16983632979782693.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983632981392348.* -> train/*/OFF_16983632981392348.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698363298496416.* -> train/*/OFF_1698363298496416.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698363298799995.* -> train/*/OFF_1698363298799995.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983632992922437.* -> train/*/OFF_16983632992922437.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698363330128268.* -> train/*/OFF_1698363330128268.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983633417752638.* -> train/*/OFF_16983633417752638.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/images/16983633439073477.png` | entfernt | Bildprüfung: verworfen (Skip) |
| 2026-11-08 | `train/images/16983633440731559.png` | entfernt | Bildprüfung: verworfen (Skip) |
| 2026-11-08 | `train/images/16983633442356699.png` | entfernt | Bildprüfung: verworfen (Skip) |
| 2026-11-08 | `train/images/16983633444036472.png` | entfernt | Bildprüfung: verworfen (Skip) |
| 2026-11-08 | `train/labels/1698363344565517.txt` | gelabelt | Bildprüfung: geprüft, 1 Rahmen |
| 2026-11-08 | `train/*/1698363356860896.* -> train/*/OFF_1698363356860896.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983633575172894.* -> train/*/OFF_16983633575172894.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983633578455703.* -> train/*/OFF_16983633578455703.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983633591575804.* -> train/*/OFF_16983633591575804.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983633614613142.* -> train/*/OFF_16983633614613142.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983633621091816.* -> train/*/OFF_16983633621091816.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698363369655661.* -> train/*/OFF_1698363369655661.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983633783522985.* -> train/*/OFF_16983633783522985.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983633785186574.* -> train/*/OFF_16983633785186574.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/images/16983633855696895.png` | entfernt | Bildprüfung: verworfen (Skip) |
| 2026-11-08 | `train/*/16983634467492864.* -> train/*/OFF_16983634467492864.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983634488801847.* -> train/*/OFF_16983634488801847.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983634490476048.* -> train/*/OFF_16983634490476048.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983634492086835.* -> train/*/OFF_16983634492086835.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983634500327604.* -> train/*/OFF_16983634500327604.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983634502141175.* -> train/*/OFF_16983634502141175.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698363450366627.* -> train/*/OFF_1698363450366627.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983634538139725.* -> train/*/OFF_16983634538139725.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983634539693725.* -> train/*/OFF_16983634539693725.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983634541356382.* -> train/*/OFF_16983634541356382.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983634543006334.* -> train/*/OFF_16983634543006334.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698363454462942.* -> train/*/OFF_1698363454462942.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983634624965363.* -> train/*/OFF_16983634624965363.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983634626579168.* -> train/*/OFF_16983634626579168.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983634628259299.* -> train/*/OFF_16983634628259299.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698363463659446.* -> train/*/OFF_1698363463659446.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698363464326071.* -> train/*/OFF_1698363464326071.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983634647990086.* -> train/*/OFF_16983634647990086.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983634656115882.* -> train/*/OFF_16983634656115882.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698363465778386.* -> train/*/OFF_1698363465778386.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698363469218298.* -> train/*/OFF_1698363469218298.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698363471513401.* -> train/*/OFF_1698363471513401.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983634772568102.* -> train/*/OFF_16983634772568102.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698363477913558.* -> train/*/OFF_1698363477913558.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698363479225769.* -> train/*/OFF_1698363479225769.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/169836348450109.* -> train/*/OFF_169836348450109.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983634897247093.* -> train/*/OFF_16983634897247093.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983634997488277.* -> train/*/OFF_16983634997488277.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983635584662342.* -> train/*/OFF_16983635584662342.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983635617278018.* -> train/*/OFF_16983635617278018.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983635620561035.* -> train/*/OFF_16983635620561035.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983635623876345.* -> train/*/OFF_16983635623876345.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983635755125186.* -> train/*/OFF_16983635755125186.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983635756787457.* -> train/*/OFF_16983635756787457.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983635758396912.* -> train/*/OFF_16983635758396912.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698363576006028.* -> train/*/OFF_1698363576006028.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983635822387006.* -> train/*/OFF_16983635822387006.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983635832181113.* -> train/*/OFF_16983635832181113.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/169836358354884.* -> train/*/OFF_169836358354884.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698363602896933.* -> train/*/OFF_1698363602896933.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983636096222236.* -> train/*/OFF_16983636096222236.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983636317654302.* -> train/*/OFF_16983636317654302.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983636319276748.* -> train/*/OFF_16983636319276748.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983636545628855.* -> train/*/OFF_16983636545628855.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983636705015314.* -> train/*/OFF_16983636705015314.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983636770341532.* -> train/*/OFF_16983636770341532.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983636832693384.* -> train/*/OFF_16983636832693384.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983636916641548.* -> train/*/OFF_16983636916641548.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698363705741118.* -> train/*/OFF_1698363705741118.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983637378880968.* -> train/*/OFF_16983637378880968.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698363754786698.* -> train/*/OFF_1698363754786698.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983637693844926.* -> train/*/OFF_16983637693844926.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983637985798488.* -> train/*/OFF_16983637985798488.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/images/16983637990696292.png` | entfernt | Bildprüfung: verworfen (Skip) |
| 2026-11-08 | `train/images/1698363806778528.png` | entfernt | Bildprüfung: verworfen (Skip) |
| 2026-11-08 | `train/labels/16983638363046334.txt` | gelabelt | Bildprüfung: geprüft, 1 Rahmen |
| 2026-11-08 | `train/images/16983639527608562.png` | entfernt | Bildprüfung: verworfen (Skip) |
| 2026-11-08 | `train/images/1698363978025693.png` | entfernt | Bildprüfung: verworfen (Skip) |
| 2026-11-08 | `train/images/16983639996725612.png` | entfernt | Bildprüfung: verworfen (Skip) |
| 2026-11-08 | `train/images/16983640000013394.png` | entfernt | Bildprüfung: verworfen (Skip) |
| 2026-11-08 | `train/images/16983640201781232.png` | entfernt | Bildprüfung: verworfen (Skip) |
| 2026-11-08 | `train/images/16983640331370738.png` | entfernt | Bildprüfung: verworfen (Skip) |
| 2026-11-08 | `train/images/16983640410063772.png` | entfernt | Bildprüfung: verworfen (Skip) |
| 2026-11-08 | `train/images/16983641033404887.png` | entfernt | Bildprüfung: verworfen (Skip) |
| 2026-11-08 | `train/images/16983642178267481.png` | entfernt | Bildprüfung: verworfen (Skip) |
| 2026-11-08 | `train/images/16983643652867787.png` | entfernt | Bildprüfung: verworfen (Skip) |
| 2026-11-08 | `train/*/1698364938284401.* -> train/*/OFF_1698364938284401.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983649387714355.* -> train/*/OFF_16983649387714355.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983649389350567.* -> train/*/OFF_16983649389350567.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983649392560227.* -> train/*/OFF_16983649392560227.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983649394357142.* -> train/*/OFF_16983649394357142.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983649397610755.* -> train/*/OFF_16983649397610755.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698364939919005.* -> train/*/OFF_1698364939919005.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698364940133101.* -> train/*/OFF_1698364940133101.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983649425340881.* -> train/*/OFF_16983649425340881.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983649427068567.* -> train/*/OFF_16983649427068567.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983649428662274.* -> train/*/OFF_16983649428662274.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698364943033833.* -> train/*/OFF_1698364943033833.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983649431959097.* -> train/*/OFF_16983649431959097.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983649433667061.* -> train/*/OFF_16983649433667061.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983649456955585.* -> train/*/OFF_16983649456955585.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983649458430862.* -> train/*/OFF_16983649458430862.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698364945985999.* -> train/*/OFF_1698364945985999.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983649476296587.* -> train/*/OFF_16983649476296587.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698364947791282.* -> train/*/OFF_1698364947791282.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983649479483888.* -> train/*/OFF_16983649479483888.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698364948120873.* -> train/*/OFF_1698364948120873.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983649495973387.* -> train/*/OFF_16983649495973387.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698365004372022.* -> train/*/OFF_1698365004372022.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/images/16983650225736203.png` | entfernt | Bildprüfung: verworfen (Skip) |
| 2026-11-08 | `train/images/16983650235597003.png` | entfernt | Bildprüfung: verworfen (Skip) |
| 2026-11-08 | `train/images/1698365051768891.png` | entfernt | Bildprüfung: verworfen (Skip) |
| 2026-11-08 | `train/*/16983655010451765.* -> train/*/OFF_16983655010451765.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983656693350236.* -> train/*/OFF_16983656693350236.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/1698365669498716.* -> train/*/OFF_1698365669498716.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983656699892716.* -> train/*/OFF_16983656699892716.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/images/1698365696065518.png` | entfernt | Bildprüfung: verworfen (Skip) |
| 2026-11-08 | `train/*/1698365697379978.* -> train/*/OFF_1698365697379978.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983656991789165.* -> train/*/OFF_16983656991789165.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |
| 2026-11-08 | `train/*/16983656996792977.* -> train/*/OFF_16983656996792977.*` | umbenannt | Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ |

## Gegenprüfung der Bildprüfung (2026-11-08)

Stichprobe: 20 zufällig gezogene geprüfte Bilder (Zufallssaat 20261108; 19 Negative, 1 mit Rahmen). Gegenprüfung durch Jan: **0 von 20 falsch** (Fehlerquote 0 

## Gegenprüfung der Bildprüfung (2026-11-08)

Stichprobe: 20 zufällig gezogene geprüfte Bilder (Zufallssaat 20261108; 19 Negative, 1 mit Rahmen). Gegenprüfung durch Jan: **0 von 20 falsch** (Fehlerquote 0 %). Bei 20 Bildern lässt sich ein Fehleranteil von bis zu rund 14 % (95-%-Grenze) nicht ausschließen, er ist aber unwahrscheinlich hoch.
