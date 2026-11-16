# Ausgabe und ISO-Zeitstempel

## Dateien und Felder

`shazam-export.csv` ist UTF-8 mit BOM, `shazam-export.json` enthält dieselben Zeilen plus Metadaten. Reihenfolge und wiederholte Erkennungen bleiben erhalten. Felder:

| Feld | Bedeutung |
|---|---|
| `position` | Fortlaufende Listenposition ab 1 |
| `timestamp` | ISO-Datum und Uhrzeit mit Minutengenauigkeit |
| `title` | Angezeigter Titel |
| `artist` | Angezeigter Künstler |
| `recognized_display` | Originale Datumsanzeige aus Shazam |
| `section` | Monats-/Jahresabschnitt oder relative Abschnittsanzeige |

Beispiel für eine ausdrücklich gewählte feste Sommerzeit: `2026-11-16T10:00+02:00`. Ohne Zeitannahme: `2026-11-16T10:00`. Das Jahr folgt dem sichtbaren Abschnitt und bei relativen Anzeigen dem ursprünglichen Gerätetag. Sekunden und eine historische Standortzeitzone sind aus der Oberfläche nicht ableitbar.

- `--offset +02:00` behandelt alle Zeiten als festen Offset, auch Winterdaten.
- `--zone Europe/Berlin` berücksichtigt Sommer-/Winterzeit. Mehrdeutige oder nicht existente Zeiten beim Zeitwechsel werden abgelehnt; für diese Daten ist eine ausdrückliche Offsetentscheidung nötig.
- Ohne diese Optionen bleibt die ISO-Zeit lokal ohne Offset.

Die JSON-Metadaten enthalten `complete`, `expected_count`, `captured_count`, `exported_at` (UTC), `reference_date` (ursprünglicher Gerätetag), `offset`, `zone` und `snapshot_count`. Teilbestände können unvollständige Positionen und `timestamp: null` enthalten; das ist keine vollständige Mediathek. Ein Import darf `complete: false` nicht als erfolgreichen Gesamtexport behandeln.

## Vorhandenen Export konvertieren

Unterstützt wird ein JSON-Export mit `rows` und den oben genannten Originalfeldern. Die ursprüngliche Datei bleibt erhalten; als Ausgabe ein neues privates Verzeichnis verwenden. Bei fehlendem ursprünglichem `reference_date` dieses ausdrücklich als `--reference-date YYYY-MM-DD` angeben.

```sh
python3 "$skill_dir/scripts/export.py" convert \
  --input "$source_json" --output "$converted_dir" --offset +02:00

python3 "$skill_dir/scripts/export.py" verify --output "$converted_dir"
```

Für saisonale Regeln stattdessen `--zone Europe/Berlin` verwenden. Keine Privacy-Mail-CSV und keine anderen CSV-Schemata als kompatibel annehmen.

## Prüfung und private Arbeitsdaten

`verify` vergleicht CSV und JSON feldweise, kontrolliert fortlaufende Positionen und Dateihashes aus `verification.json`. Ein als vollständig markierter Export muss die erwartete Anzahl, alle Pflichtfelder und ISO-Zeitstempel enthalten. Eine bestandene Teilbestandsprüfung bestätigt lediglich die Dateikonsistenz. Die Prüfsummen sind eine Konsistenzprüfung, keine unabhängige Signatur.

`checkpoint.json`, `snapshots/`, `probe.json`, `devices.json`, `screen-state.json` und `mobile-stderr.log` bleiben privat. Sie ermöglichen Wiederaufnahme und Diagnose; nach erfolgreicher Abnahme kann der Nutzer sie entfernen. Der Export enthält keine Audiodateien oder Track-URLs.
