---
name: shazam-export
description: Exportiert die Shazam-Mediathek eines Android-Geräts über den vorhandenen Mobile MCP als CSV und JSON, setzt unterbrochene Exporte fort und ergänzt ISO-Zeitstempel.
---

# Shazam exportieren

Nutze die mitgelieferten Skripte für die positionsgetreue Auslesung der deutschen Android-Shazam-Oberfläche. Die Reihenfolge und wiederholte Erkennungen desselben Titels gehören zum Export.

Für Gerätewahl, Startprofil, Export und Wiederaufnahme lies [references/run.md](references/run.md). Für eine reine ISO-Konvertierung oder die Interpretation und Prüfung bestehender Dateien lies [references/output.md](references/output.md).

## Durchführung

- Verwende den vorhandenen Original-[Mobile MCP](https://github.com/mobile-next/mobile-mcp). Das Plugin installiert weder MCP noch Android-SDK oder Emulator und verändert keine Clientkonfiguration. Ein privates Startprofil verbindet die Skripte mit der vorhandenen Runtime.
- Wähle das Android-Gerät ausdrücklich aus der privaten Inventur. Shazam muss angemeldet sein und seine Songliste zeigen; einen neuen Export oben in der Liste beginnen. Entsperren übernimmt der Nutzer.
- Schreibe Titel, Snapshots, Logs, Inventur und Startprofil in ein privates Verzeichnis außerhalb des Plugins und aller Git-Repositories. Keine persönlichen Daten als Beispiele veröffentlichen.
- Kündige die vorübergehende USB-Wachhaltung an. Das Skript sichert die Einstellung und stellt sie bei Abschluss, Pause und Abbruch zurück. Nach einem Prozessabsturz das gespeicherte Journal über `restore-display` wiederherstellen; keinen fremden Einstellungswert überschreiben. Bei gewünschtem Verzicht `--no-keep-awake` verwenden.
- Übernimm die Zeitannahme des Nutzers. `--offset +02:00` bedeutet feste Sommerzeit für alle Einträge; `--zone Europe/Berlin` berücksichtigt Jahreszeiten. Ohne Vorgabe bleiben ISO-Zeiten lokal ohne Offset. Keine unbekannten Jahre, Sekunden oder Zeitzonen ergänzen.

## Vollständigkeit

Die Skripte lesen die Gesamtzahl aus Shazam, warten auf Ladeplatzhalter und scrollen anhand frischer Listenbounds außerhalb des Fastscroll-Bereichs. Sie ordnen überlappende Ansichten nach Positionen zu; gleiche Titel dürfen mehrfach vorkommen. Bei fehlender Überlappung ist die Rücksuche begrenzt.

Eine Pause bedeutet einen Teilbestand: Checkpoints und originale Datumsanzeigen erhalten, Ursache beheben und `resume` verwenden. Bei unbekanntem Layout, gesperrtem Gerät, geändertem Bestand oder mehrdeutiger Zuordnung den Fehler melden. Keinen Checkpoint löschen oder `complete` manuell setzen. Erst nach bestätigtem Listenende, erreichter Gesamtzahl und erfolgreichem `verify` einen vollständigen Export melden.

Der Auftrag umfasst Lesen am Telefon und lokale Exportdateien. NAS-Import, Cloud-Synchronisierung oder Änderungen der Shazam-Mediathek brauchen einen entsprechenden Nutzerauftrag.
