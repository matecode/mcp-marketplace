# Bandcamp MCP

Bandcamp nach Künstlern, Labels, Alben und Tracks durchsuchen und vollständige
HTTPS-Weblinks erhalten. Öffentliche Adresse:
**https://mcp.bunteban.de/bandcamp/mcp**. Pluginversion 0.1.0.

Ein eigenständiger Dienst. Er benötigt kein Bandcamp-Konto oder API-Key.
Der Zugang zum MCP erfolgt über die persönliche Authentik-Freigabe.

## Einrichtung durch den Nutzer

In Claude Code:

```sh
claude plugin marketplace add https://github.com/matecode/mcp-marketplace.git
claude plugin install bandcamp-mcp@mate-mcp
```

In einer neuen Sitzung `/mcp` öffnen und Bandcamp selbst bei Authentik anmelden.
Bei einem bereits eingebundenen Marketplace dessen Katalog aktualisieren und
das Plugin auswählen.

In Codex CLI oder über den Marketplace in Codex Desktop:

```sh
codex plugin marketplace add https://github.com/matecode/mcp-marketplace.git
codex plugin add bandcamp-mcp@mate-mcp
codex mcp login bandcamp --scopes openid,profile,email,offline_access,bandcamp
```

Alternativ ohne Plugin, als separater Codex-MCP:

```sh
codex mcp add bandcamp --url https://mcp.bunteban.de/bandcamp/mcp
codex mcp login bandcamp --scopes openid,profile,email,offline_access,bandcamp
```

Einen Installationsweg wählen, damit kein doppelter Eintrag entsteht. Für Claude
Web/App oder andere Remote-Clients die MCP-Adresse eintragen und selbst anmelden.
Benötigte Scopes: `openid profile email offline_access bandcamp`. Dynamische
Clientregistrierung; keine eigene Client-ID oder Clientsecret eintragen.
Anmeldung und Zustimmung übernimmt der Nutzer. Paket- und Serverprüfungen
belegen noch keine persönliche Clientnutzung oder Langzeit-Refreshfunktion.

## Werkzeuge

| Werkzeug | Zweck |
|---|---|
| `bandcamp_search` | Suchtext, Typ `all/track/album/artist/label`, 1–50 Treffer mit Links |
| `bandcamp_search_link` | Such-Weblink ohne Netzwerkzugriff erzeugen |
| `bandcamp_get_album` | Albumdetails mit Tracklinks lesen |
| `bandcamp_get_track` | Trackdetails mit Albumlink lesen |
| `bandcamp_get_artist` | Künstlerdetails und Veröffentlichungen lesen |

Beispiel: „Suche auf Bandcamp nach Burial und gib mir fünf Tracklinks.“
Mit einem gefundenen Link anschließend Details abrufen. Suchranking allein
bestätigt keine exakte Übereinstimmung von Künstler, Version und Titel.

Die Suche liefert immer `search_url`. `ok` enthält Treffer; `empty` ist eine
erfolgreiche Suche ohne Treffer. `blocked`, `format_changed` oder `unavailable`
kennzeichnen einen fehlgeschlagenen Abruf. Dann den Suchlink im Browser öffnen;
eine eventuell verlangte Browserprüfung bleibt dort nötig.

## Grenzen

Bandcamp bietet hierfür keine öffentliche versionierte Katalog-API. Der Dienst
nutzt die interne Suchschnittstelle und öffentlich abrufbare Detailseiten über
[bandcamp-mcp 0.1.2](https://github.com/Venut-Technologies/bandcamp-mcp).
Bandcamps Bot-Prüfung kann Suche oder Details jederzeit einschränken.
Es werden keine Prüfungen umgangen. Eigene Künstlerdomains werden nicht
abgerufen; bei fehlendem Slug bleibt `url` unbekannt. Links werden aus vorhandenen
Slugs abgeleitet und niemals aus Künstler- oder Titelnamen erfunden.

Keine Käufe, Audiodownloads oder Kontoverwaltung. Suchtexte und Ergebnisse werden
vom MCP nicht dauerhaft gespeichert. Bandcamp erhält die Suchanfrage.
