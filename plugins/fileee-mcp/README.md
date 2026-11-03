# Fileee MCP

Persönliche Fileee-Dokumente über `https://mcp.bunteban.de/fileee/mcp` nutzen. Der Betreiber muss den eigenen Fileee-Zugang zuvor freigeben und zuordnen. Die Anmeldung erfolgt mit Authentik; ein Marketplace-Download allein gewährt keinen Dokumentzugriff.

Clienteinrichtung und Anmeldung übernimmt der Nutzer selbst. Für Claude Web/App den unten beschriebenen Remote-Connector verwenden. Der Marketplace-Eintrag `fileee-mcp` ist zusätzlich als Plugin für Codex und Claude Code verfügbar.

## Anmeldung

Der Server verwendet die native OAuth-Anbindung des Fileee-Projekts. Der registrierte öffentliche Client heißt `fileee-mcp`; ein Client-Secret wird nicht benötigt. OAuth-Nachweise gehören in den geschützten Anmeldespeicher des jeweiligen Clients.

Codex verwendet ab Paket 0.1.1 `mcp.codex.json` mit `oauth.client_id`, `callback_port: 8766` und einer Scope-Liste. Dieses Format ist mit Codex CLI 0.163.0-alpha.10.2 geprüft; die portable Client-ID aus Paket 0.1.0 wurde dort nicht übernommen und führte zu „Dynamic client registration not supported“. Claude Code verwendet `.mcp.json` mit `oauth.clientId`, Callbackport 8767 und Scopes als Zeichenkette. Beide melden sich unabhängig an. Für die Installation die bestehende [Marketplace-Anleitung](../../README.md) verwenden.

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
- Authentifizierung: **Jetzt anmelden**
- OAuth-Client: **Eigenen OAuth-Client verwenden**
- OAuth Client ID: `fileee-mcp`
- OAuth Client Secret: leer

Fileee verwendet einen bereits registrierten öffentlichen OAuth-Client und bietet in diesem Aufbau keine dynamische Clientregistrierung (DCR). Deshalb **„Eigenen OAuth-Client verwenden“** wählen. Bei anderen MCPs mit DCR kann Claude stattdessen **„Automatisch registrieren“** verwenden. Die Anzeige „Erkannt“ ist hier erwartbar: OAuth wird erkannt, die feste Client-ID muss noch eingetragen werden. Eine leere Client-ID verhindert das Hinzufügen; das ist kein Nachweis eines fehlgeschlagenen Logins. Die Client-ID ist eine öffentliche Kennung und kein persönliches Fileee-Zugangsmittel.

Den Connector verbinden und die Authentik-Anmeldung durchführen. Anschließend in der App dasselbe Claude-Konto verwenden und den Fileee-Connector im Chat aktivieren. Claude Web/App verwendet einen eigenen Anmeldevorgang; eine erfolgreiche Codex-Anmeldung ist dafür kein Funktionsnachweis. Der Server selbst wird durch die Connector-Anmeldung nicht installiert oder aktualisiert.

## Funktionen und Grenzen

Upstream 0.9.4 beschreibt 44 Werkzeuge: 32 lesende, 8 schreibende und 4 Betriebswerkzeuge. Darunter sind Dokumentensuche, Metadaten, OCR, PDF-/Seitenbilder, Upload und Dokumentbearbeitung, Kontakte, Erinnerungen und Boxzuordnungen. Teilen und dauerhaftes Löschen sind in diesem Stand noch keine Werkzeuge. PDF-/Bildabrufe sind auf 8 MiB begrenzt.

**Der Seitenzugriff ist korrigiert; die tatsächliche Claude-Inhaltsauswertung bleibt zu prüfen.** Metadaten und Volltext-Suchtreffer funktionieren laut Nutzerbericht vom 2026-11-03. Das ursprünglich eingesetzte `get_document` lieferte nur `pageCount`; der veröffentlichte Dienst enthält jetzt den getesteten Seitenmetadaten-Fix `0.9.4-pages1`. `get_document` liefert ein geordnetes `pages`-Array mit echten `id`-Werten und numerischer `imageVersion`. IDs nicht aus Dokument-IDs ableiten oder erraten. `get_document_pdf` liefert eine eingebettete `application/pdf`-Binärressource, die Claude laut Bericht nicht unterstützt; dieses Problem ist auch in [Upstream #83](https://github.com/strausmann/fileee-mcp-server/issues/83) offen dokumentiert. Das Vorhandensein der Werkzeuge bestätigt daher keine vollständige Inhaltsauswertung. Der [Upstream-PR #96](https://github.com/strausmann/fileee-mcp-server/pull/96) ist eingereicht. Serverseitig ist OCR-Abruf mit leerem Text und eine vollständige JPEG-Seite erfolgreich geprüft. Im Claude-Connector die aktualisierte Werkzeugbeschreibung neu laden und einen neuen Chat verwenden: `get_document` → `pages[].id` → `get_page_ocr`. Für `get_page_image` unmittelbar zuvor `get_document` erneut lesen und `pages[].id` sowie `pages[].imageVersion` als `pageId`/`version` verwenden. Die PDF-Clientgrenze bleibt bestehen.

Der vollständige Katalog wird angeboten; ToolAnnotations beschreiben Lese-/Schreibverhalten. Zustimmung zu Änderungen wird im Client verwaltet und nicht durch diese Hinweise technisch erzwungen. Zugangsdaten- und Kontozuordnungsänderungen übernimmt der Betreiber bei einem gezielten Fileee-Dienstneustart.

Stand 2026-11-03: Dienst öffentlich aktiv, tatsächlicher Katalog mit 44 Werkzeugen und persönliche Kontostatus-Leseprobe erfolgreich geprüft. Paket 0.1.1 in isolierten Codex-/Claude-Code-Konfigurationen geladen; beide frischen OAuth-Anmeldungen erfolgreich. Codex zusätzlich mit nativem Kontostatus-Werkzeugaufruf und kontrolliert ausgelöstem nativem Refresh geprüft. Keine persönliche Clientkonfiguration verändert. Der gepinnte Seitenfix ist auf dem Dienst aktiviert und intern/öffentlich durch eine reale Ein-Seiten-Probe geprüft. Die Einrichtung in Claude Web/App übernimmt der Nutzer selbst; Metadaten-/Suchzugriff durch Nutzerbericht bestätigt, tatsächliche Inhaltsauswertung nach dem Fix und Refresh dort weiterhin offen.

Quellen: [Fileee-Projekt](https://github.com/strausmann/fileee-mcp-server), [Authentik-Anleitung](https://github.com/strausmann/fileee-mcp-server/blob/v0.9.4/docs/idp/authentik.md), [Codex-Plugins](https://developers.openai.com/codex/plugins/build), [Claude-Code-MCP](https://code.claude.com/docs/en/mcp).
