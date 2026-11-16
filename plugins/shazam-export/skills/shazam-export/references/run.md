# Android-Export durchführen

## Voraussetzungen und erprobte Umgebung

Python 3.11+, Node.js 20+, ADB und eine vorhandene Installation des Original-[Mobile MCP](https://github.com/mobile-next/mobile-mcp). V1 unterstützt die deutsche Shazam-Songliste auf Android ohne Root. Das physische Vorbild wurde mit einem Pixel auf macOS/Apple Silicon, Mobile MCP 1.0.17 und mobilecli 1.0.23 erprobt. Ein Pin der MCP-Version allein fixiert nicht alle transitiven Abhängigkeiten. Andere Plattformen und App-Sprachen sind noch nicht physisch geprüft.

USB-Debugging muss am ausgewählten Gerät für den Rechner freigegeben sein. Der Nutzer öffnet Shazam und die vollständige Songliste. Ein Emulator ist nur nutzbar, wenn Shazam darin bereits läuft, angemeldet ist und den gewünschten Bestand synchronisiert hat. Der Skill installiert keine Zusatzapps.

## Privates Startprofil

Die Skripte öffnen eine eigene stdio-Verbindung zur vorhandenen Mobile-MCP-Runtime. Aus dem bereits eingerichteten Clienteintrag nur dessen `command`, `args`, optional `env` und `cwd` in ein privates JSON-Profil übernehmen. Beispiel mit Platzhalter:

```json
{
  "command": "node",
  "args": ["/ABSOLUTER/PFAD/mobile-mcp/lib/index.js"],
  "env": {
    "MOBILEMCP_DISABLE_TELEMETRY": "1",
    "MOBILEWRIGHT_DISABLE_TELEMETRY": "1"
  }
}
```

Falls die vorhandene Installation `MOBILECLI_PATH` oder einen besonderen `PATH` benötigt, diese Werte übernehmen. Beide Telemetrie-Abschaltungen werden zusätzlich vom Skript erzwungen. Das Profil außerhalb des Plugins und Git halten; keine gesamte Clientkonfiguration kopieren oder veröffentlichen. Ein vorhandener absoluter Node-Pfad ist zulässig. `npx` ist nur eine vom Nutzer autorisierte Alternative, da es Pakete herunterladen kann; keine stillen Downloads für einen Export.

## Befehle

`skill_dir` bezeichnet den installierten Skillordner mit `SKILL.md`, `launch_file` das private JSON-Profil, `export_dir` ein privates Verzeichnis außerhalb des Plugins und aller Git-Repositories, `adb_path` den vorhandenen ADB-Pfad. Die Variablen mit den tatsächlichen Pfaden setzen. Gerätekennung privat aus `devices.json` lesen und ausdrücklich als `device_id` wählen; keine automatische Wahl des ersten Geräts.

```sh
python3 "$skill_dir/scripts/export.py" devices \
  --output "$export_dir" --mcp-launch "$launch_file"

python3 "$skill_dir/scripts/export.py" probe \
  --output "$export_dir" --mcp-launch "$launch_file" \
  --device "$device_id" --adb "$adb_path"
```

`devices` speichert die Inventur privat, `probe` liest die sichtbaren Songzeilen. Beide geben auf stdout nur technische Angaben aus. Die Probe scrollt nicht und verändert keine Display-Einstellung. Die App im Vordergrund allein beweist keinen entsperrten Bildschirm.

Neuen Lauf oben in der Songliste starten. Die Titelzahl wird aus Shazam gelesen. Das folgende Beispiel verwendet die ausdrücklich gewählte Annahme fester Sommerzeit:

```sh
python3 "$skill_dir/scripts/export.py" export \
  --output "$export_dir" --mcp-launch "$launch_file" \
  --device "$device_id" --adb "$adb_path" --offset +02:00

python3 "$skill_dir/scripts/export.py" resume \
  --output "$export_dir" --mcp-launch "$launch_file" \
  --device "$device_id" --adb "$adb_path"

python3 "$skill_dir/scripts/export.py" verify --output "$export_dir"
```

`resume` übernimmt Datum und Zeitannahme aus dem Checkpoint. Es verlangt dasselbe Gerät, denselben Gerätetag und dieselbe App-Version. Die aktuelle Ansicht muss den bereits erfassten Bestand überlappen; andernfalls sucht das Skript höchstens acht kleine Rückscrollschritte. Bei einer Pause zur letzten erfassten Ansicht zurückkehren und erneut fortsetzen. Nach einem Datumswechsel oder App-/Bestandsänderung einen neuen Lauf in einem neuen Verzeichnis beginnen; vorhandene Teilbestände behalten.

Pro Ansicht gibt es höchstens sechs Ladeversuche. `--max-pages` begrenzt den Lauf (Standard 2000); `--no-keep-awake` verzichtet auf die temporäre Wachhaltung. Fortschritt und Exporte werden alle fünf akzeptierten Ansichten gespeichert, zusätzlich bei regulärem Abbruch. Vollständigkeit verlangt die gemeldete Anzahl vollständiger Positionen und zwei weitere unveränderte Endansichten.

## Bildschirm wiederherstellen und Pausen

USB-Wachhaltung wird in `screen-state.json` protokolliert und im `finally` zurückgestellt. Nach einem harten Prozessabsturz:

```sh
python3 "$skill_dir/scripts/export.py" restore-display \
  --output "$export_dir" --device "$device_id" --adb "$adb_path"
```

Das Journal ist an das Gerät gebunden. Bei einer inzwischen unabhängig geänderten Einstellung stoppt die Wiederherstellung. Ein lebender Prozess in `run.lock` verhindert parallele Läufe im selben Verzeichnis; ein nachweislich toter PID-Lock kann automatisch entfernt werden. Keinen Lock eines laufenden Exports löschen.

Exitcode 2 bedeutet Pause oder ungültige Eingabe, 130 einen Benutzerabbruch. Häufige Pausecodes:

| Code | Nächster Schritt |
|---|---|
| `device_locked` / `selected_device_not_authorized` | Nutzer entsperrt bzw. bestätigt USB-Debugging |
| `start_at_top_of_song_list` | Neuen Lauf am Listenanfang beginnen |
| `song_rows_still_loading` | App fertig laden lassen und fortsetzen |
| `no_positional_overlap` / `ambiguous_positional_overlap` | Zur letzten erfassten Ansicht zurückkehren; keine Zuordnung erfinden |
| `list_end_with_missing_positions` | Teilbestand behalten; fehlende Positionen untersuchen |
| `song_count_changed` / `shazam_version_changed_since_checkpoint` | Neuen Lauf in neuem Verzeichnis beginnen |
| `mcp_timeout` / `mobile_tool_failed` | Private Laufzeitlogs prüfen, Verbindung wiederherstellen |
| `display_setting_changed_independently` | Einstellung am Gerät prüfen; keinen fremden Wert überschreiben |

Unbekannte Shazam-Layouts werden abgelehnt. Die Rohansichten dienen der Diagnose, werden aber nicht als Titel im Chat ausgegeben. ISO-Konvertierung vorhandener JSON-Exporte steht in [output.md](output.md); Shazams Privacy-Mail-CSV ist kein unterstütztes Eingabeschema.
