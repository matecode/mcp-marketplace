# Fileee MCP

Persönliche Fileee-Dokumente über `https://mcp.bunteban.de/fileee/mcp` nutzen. Der Betreiber muss den eigenen Fileee-Zugang zuvor freigeben und zuordnen. Die Anmeldung erfolgt mit Authentik; ein Marketplace-Download allein gewährt keinen Dokumentzugriff.

## Anmeldung

Der Server verwendet die native OAuth-Anbindung des Fileee-Projekts. Der registrierte öffentliche Client heißt `fileee-mcp`; ein Client-Secret wird nicht benötigt. OAuth-Nachweise gehören in den jeweiligen Client-Schlüsselbund.

Codex verwendet `mcp.codex.json` mit dem dokumentierten `com.openai`-OAuth-Format. Claude Code verwendet `.mcp.json` mit `oauth.clientId`. Beide melden sich unabhängig an und erhalten denselben persönlichen Werkzeugzugang. Für die Installation die bestehende [Marketplace-Anleitung](../../README.md) verwenden.

Für eine direkte Einrichtung ohne Plugin:

```sh
codex mcp add fileee --url https://mcp.bunteban.de/fileee/mcp --oauth-client-id fileee-mcp
codex mcp login fileee --scopes openid,profile,email,offline_access,fileee
```

```sh
claude mcp add --transport http --client-id fileee-mcp --callback-port 8767 fileee https://mcp.bunteban.de/fileee/mcp
```

In Claude Code anschließend `/mcp` öffnen und anmelden.

## Claude Web, Desktop und Mobile

In den Einstellungen einen benutzerdefinierten Remote-Connector hinzufügen:

- Name: `Fileee`
- URL: `https://mcp.bunteban.de/fileee/mcp`
- OAuth Client ID: `fileee-mcp`
- OAuth Client Secret: leer

Danach die Authentik-Anmeldung durchführen. Claude Web/App verwendet einen eigenen Anmeldevorgang; eine erfolgreiche Codex-Anmeldung ist dafür kein Funktionsnachweis. Der Server selbst wird durch die Connector-Anmeldung nicht installiert oder aktualisiert.

## Funktionen und Grenzen

Upstream 0.9.4 beschreibt 44 Werkzeuge: 32 lesende, 8 schreibende und 4 Betriebswerkzeuge. Darunter sind Dokumentensuche, Metadaten, OCR, PDF-/Seitenbilder, Upload und Dokumentbearbeitung, Kontakte, Erinnerungen und Boxzuordnungen. Teilen und dauerhaftes Löschen sind in diesem Stand noch keine Werkzeuge. PDF-/Bildabrufe sind auf 8 MiB begrenzt.

Der vollständige Katalog wird angeboten; ToolAnnotations beschreiben Lese-/Schreibverhalten. Zustimmung zu Änderungen wird im Client verwaltet und nicht durch diese Hinweise technisch erzwungen. Zugangsdaten- und Kontozuordnungsänderungen übernimmt der Betreiber bei einem gezielten Fileee-Dienstneustart.

Stand 2026-11-03: Offline-Katalogprüfung und strenge Claude-Validierung bestanden. Fileee-Paket in isoliertem Codex CLI 0.163.0-alpha.10.2 und Claude Code 2.1.285 installiert; beide erkennen die vorgesehene Verbindung, Claude einschließlich öffentlicher Client-ID und Scopes. Keine persönlichen Clienteinstellungen verändert. Dienstaktivierung und persönliche Kontoeinrichtung sowie tatsächlicher Werkzeugkatalog, Fileee-Leseprobe und OAuth/Refresh in allen gewünschten Clients stehen noch aus.

Quellen: [Fileee-Projekt](https://github.com/strausmann/fileee-mcp-server), [Authentik-Anleitung](https://github.com/strausmann/fileee-mcp-server/blob/v0.9.4/docs/idp/authentik.md), [Codex-Plugins](https://developers.openai.com/codex/plugins/build), [Claude-Code-MCP](https://code.claude.com/docs/en/mcp).
