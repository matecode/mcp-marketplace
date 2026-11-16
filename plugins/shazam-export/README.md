# Shazam exportieren 0.1.0

Skill für den lokalen Export der Shazam-Mediathek eines Android-Geräts als CSV und JSON. Er bewahrt Reihenfolge und wiederholte Erkennungen, speichert Checkpoints und prüft die Vollständigkeit anhand der in Shazam angezeigten Titelzahl.

## Installation

Nach Registrierung des [Mate-Marketplace](../../README.md):

```sh
codex plugin add shazam-export@mate-mcp
```

Für Claude Code:

```sh
claude plugin install shazam-export@mate-mcp
```

Aufruf in Codex: „Nutze `$shazam-export`, um meine Shazam-Mediathek vom Android-Gerät als CSV und JSON zu exportieren.“ Claude Code stellt den Skill unter dem Plugin-Namespace bereit.

## Voraussetzungen und Verwendung

Vorhandener Original-[Mobile MCP](https://github.com/mobile-next/mobile-mcp), Python 3.11+, Node.js 20+ und ADB. Android-Gerät per USB anschließen, USB-Debugging freigeben und Shazam angemeldet mit geöffneter Songliste bereithalten. V1 unterstützt die deutsche Oberfläche. [Startprofil, Gerätewahl und Befehle](skills/shazam-export/references/run.md).

Das Plugin bündelt einen Skill mit portablen Skripten und startet dafür eine Verbindung zur vorhandenen lokalen Mobile-MCP-Runtime. Es benötigt keinen eigenen OAuth-Login oder Remote-Dienst. Es installiert keine Runtime und ändert keine persönliche Clientkonfiguration. Ein auf dem Rechner angeschlossenes Telefon ist aus einer Cloud-Sitzung nicht automatisch erreichbar.

Während des Exports wird das Telefon bei USB-Verbindung vorübergehend wach gehalten; die ursprüngliche Einstellung wird zurückgestellt. Titel und Diagnoseartefakte bleiben in einem ausdrücklich gewählten privaten Ausgabeverzeichnis außerhalb des Plugins und aller Git-Repositories.

ISO-Zeitstempel sind minutengenau. `--offset +02:00` setzt die gewählte feste Sommerzeit auf alle Einträge; `--zone Europe/Berlin` berücksichtigt Jahreszeiten. Ohne Vorgabe bleiben Zeiten lokal ohne Offset. [Ausgabeformat, Konvertierung und Prüfung](skills/shazam-export/references/output.md).

## Prüfung

```sh
python3 -m unittest discover -s plugins/shazam-export/tests -v
python3 scripts/check-marketplace.py
claude plugin validate plugins/shazam-export --strict
```

Abnahme am 16.11.2026:

- 21 synthetische Verhaltenstests bestanden: Platzhalter, Wiederholungen, Wiederaufnahme, Abbruch, Bildschirmwiederherstellung, Zeitwechsel, Dateikonsistenz und echter stdio-Transport mit synthetischem Server.
- Alle 426 privaten Ansichten des zuvor erfolgreichen Pixel-Exports offline rekonstruiert: 1.463 Positionen und sämtliche Originalfelder/ISO-Zeitstempel identisch. Keine privaten Daten im Paket.
- Vorhandenen vollständigen JSON-Export über die neue CLI in ein neues privates Verzeichnis konvertiert; CSV/JSON und feste `+02:00` geprüft, Quelle erhalten.
- Katalogprüfung, strenge Claude-Validierung und Skill-Validator bestanden. Claude Code 2.1.285 und Codex CLI 0.160.0 installierten das Paket in isolierten temporären Konfigurationen. Claude erkennt einen Skill und null MCP-Server; Codex cached den Skill und lädt keine MCP-Verbindung.
- Vorhandener Mobile MCP 1.0.17 über das private Startprofil initialisiert und Geräteinventur gelesen. Bei dieser neuen Probe war nur der Emulator verbunden; eine neue physische Pixel-Probe des finalen Pakets ist daher unbestätigt. Der erfolgreiche physische Export stammt vom Vorläufer auf macOS/Apple Silicon.

Persönliche Plugininstallation und die Anzeige in Codex Desktop übernimmt der Nutzer. Claude Web/Cowork und andere App-Sprachen sind nicht geprüft.
