# Home Assistant MCP

Verbindung: `https://mcp.bunteban.de/homeassistant/mcp`.

Mit dem eigenen Home-Assistant-Konto unter `https://ha.bunteban.de` anmelden. Client-ID, Client-Secret und zusätzliche Scopes leer lassen; der Original-Webhook-Proxy vermittelt HA-OAuth. Kein persönlicher HA-Token in OpenBao nötig. Keine Tokens im Chat eingeben. Die Werkzeugrechte folgen dem HA-Zugang der Server-App; die Anmeldung erzeugt keine individuelle Werkzeug-Allowlist.

Ab Plugin **0.3.0** ist die Verbindung auf die Original-HA-Apps mit HA-OAuth umgestellt. Bestehende Clients müssen erneut bei Home Assistant autorisiert werden; alte Authentik-Tokens funktionieren an diesem Endpunkt nicht. In Codex bei Problemen die dynamische Registrierung verwenden: `codex mcp login homeassistant --oauth-client-registration dcr` (Servernamen aus der eigenen Konfiguration verwenden).

Verbindungsprüfung am 2026-10-18: Originalserver `ha-mcp` 8.7.0, 83 Werkzeuge, HA-OAuth-Login, lesende Systemübersicht und erneuter Zugriff nach OAuth-Refresh erfolgreich. Anonyme Zugriffe und ungültige Tokens werden mit 401 verweigert; Ressourcenmetadaten nennen die feste MCP-Adresse. Keine Geräte als Test geschaltet. OAuth bleibt laut Upstream Beta; Claude-/ChatGPT-Clientanmeldung und deren eigener Refresh sind separat zu prüfen. Keine Claude-Web-Installation vorgenommen.

Das Plugin verbindet den vorhandenen Original-HA-MCP. Alle angebotenen Werkzeuge sind verfügbar, einschließlich Gerätesteuerung und administrativer Änderungen mit den Rechten der Server-App.

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
