# Home Assistant MCP

Verbindung: `https://mcp.bunteban.de/homeassistant/mcp`.

Mit Authentik anmelden; die Freigabegruppe für Home Assistant ist erforderlich. Jeder Nutzer hinterlegt seinen eigenen HA-Token im persönlichen OpenBao-Eintrag, Feld `token`. `homeassistant_connection_status` zeigt den passenden Einrichtungslink. Die OpenBao-Oberfläche ist nur im Heimnetz oder per bestehendem VPN erreichbar. Keine Tokens im Chat eingeben.

Die Werkzeuge verwenden ausschließlich den persönlichen HA-Token und dessen Rechte. Das Plugin richtet weder einen HA-Server noch ein HA-Konto ein. Alle angebotenen HA-MCP-Werkzeuge sind verfügbar, einschließlich Gerätesteuerung und administrativer Änderungen, soweit das persönliche HA-Konto sie erlaubt.

Installation, OAuth-Anmeldung, Werkzeugfunktion und Refresh sind getrennte Prüfungen. Bei bereits vorhandenem separat eingerichteten Home-Assistant-MCP zunächst doppelte Verbindungen vermeiden.

## Skill aus dem Video

Das Plugin enthält den in [simon42s Video ab 20:43](https://www.youtube.com/watch?v=AL391nkWGIc&t=1243s) empfohlenen **`home-assistant-best-practices`** aus [homeassistant-ai/skills](https://github.com/homeassistant-ai/skills). Die Videobeschreibung nennt ihn als „Agent Skills / Best-Practice-Skill“. Es handelt sich um einen Skill mit 15 Referenzdateien, nicht um mehrere getrennte Skills.

Mit Version **0.2.0** werden MCP-Verbindung und Skill gemeinsam installiert. Claude Code und Codex entdecken ihn aus `skills/home-assistant-best-practices/SKILL.md`; er wird bei passenden Home-Assistant-Aufgaben automatisch berücksichtigt. Eine zusätzliche ZIP-Installation ist dafür nicht nötig. Wer den offiziellen Skill bereits separat installiert hat, sollte doppelte Skill-Installationen vermeiden.

Die Empfehlungen betreffen native Trigger und Bedingungen, Helper statt unnötiger Templates, passende Automation-Modi, Geräte- und Szenensteuerung, Dashboards, Blueprints, AppDaemon, Backups und sichere Änderungen bestehender Konfigurationen. Der Skill beschreibt auch Funktionen, die zusätzliche HA-Komponenten oder Berechtigungen benötigen; seine Installation richtet diese nicht automatisch ein.

Originalinhalt unverändert gebündelt: Upstream-Version **0.51.0**, Commit [`68f2690`](https://github.com/homeassistant-ai/skills/tree/68f2690ff868cde35f4e755cde82a69666f89b06), MIT-Lizenz im Skill-Verzeichnis. `upstream-skill.json` dokumentiert Quelle und SHA-256 aller übernommenen Dateien. Updates werden gezielt geprüft und mit einer neuen Plugin-Version veröffentlicht; sie folgen nicht automatisch dem Upstream-Branch.

Bestehendes Plugin aktualisieren:

```sh
claude plugin marketplace update mate-mcp
claude plugin update homeassistant-mcp@mate-mcp
codex plugin marketplace upgrade mate-mcp
codex plugin add homeassistant-mcp@mate-mcp
```

Den jeweiligen Client anschließend neu laden oder eine neue Sitzung starten. Dies ist eine Paketaktualisierung für Claude Code/Codex; kein Eintrag in Claude Web wurde vorgenommen.


Paketprüfung am 2026-10-18: Marketplace-Konsistenz, strenge Claude-Manifestvalidierung und Skill-Frontmatter geprüft. Claude Code erkennt in isolierter Installation einen Skill und einen MCP-Server. Codex installiert Version 0.2.0 und listet den aktivierten Skill über `skills/list` als `homeassistant-mcp:home-assistant-best-practices` aus dem Plugin-Cache. Dies bestätigt Erkennung; eine modellgestützte HA-Aufgabe mit dem Skill wurde nicht ausgeführt. Persönliche Clientkonfigurationen und NAS-Dienste wurden nicht geändert.
