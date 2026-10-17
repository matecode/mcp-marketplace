# Mate MCP Marketplace

Öffentlicher GitHub-Marketplace für **Claude Code** und **Codex CLI/Desktop**, Repository `matecode/mcp-marketplace`, Marketplace-ID `mate-mcp`, Version 0.1.0.

## Plugins

| Plugin-ID | Dienst | MCP-Adresse |
|---|---|---|
| `mail-mcp` | Mail und Sieve | `https://mcp.bunteban.de/mail/mcp` |
| `calendar-mcp` | Kalender und Kontakte | `https://mcp.bunteban.de/calendar/mcp` |
| `obsidian-mcp` | Obsidian-Vault | `https://mcp.bunteban.de/obsidian/mcp` |
| `kleinanzeigen-mcp` | Kleinanzeigen | `https://mcp.bunteban.de/kleinanzeigen/mcp` |
| `lizu-mcp` | Nextcloud | `https://mcp.bunteban.de/lizu/mcp` |

Jedes Plugin lässt sich einzeln installieren. Die Pakete starten keine lokalen Server; sie verbinden die bestehenden Homelab-Dienste über Streamable HTTP.

## Voraussetzungen

Der öffentliche Katalog kann über HTTPS ohne GitHub-Konto oder Git-Zugangsdaten geladen werden. Für diesen Weg die vollständige HTTPS-Repository-Adresse verwenden. Bei optionalem SSH-Zugang muss der Schlüssel bereits nutzbar und der GitHub-Hostschlüssel bekannt sein; Hostschlüsselprüfung nicht abschalten. Keine Tokens in Remote-URLs oder Manifesten eintragen.

GitHub-Zugriff und MCP-Zugriff sind unabhängig: Über Authentik persönlich anmelden und die jeweilige Dienstfreigabe erhalten. Mail/Kalender und LiZu brauchen die eigenen Kontoeinträge in der vorgesehenen OpenBao-Verwaltung. Obsidian bleibt an den freigegebenen Betreiber-Vault gebunden; eine Marketplace-Installation erzeugt keinen eigenen Vault. Kleinanzeigen verwendet die bestehende dienstspezifische Kontozuordnung.

## Claude Code

```sh
claude plugin marketplace add https://github.com/matecode/mcp-marketplace.git
claude plugin install mail-mcp@mate-mcp
```

Alternativ mit explizitem SSH-Remote:

```sh
claude plugin marketplace add git@github.com:matecode/mcp-marketplace.git
```

Weitere Plugin-IDs aus der Tabelle einzeln installieren. In einer neuen Sitzung `/mcp` öffnen und den gewünschten Server authentifizieren. `/plugin` zeigt die installierten Plugins. Die `.mcp.json` enthält die vom jeweiligen Server benötigten OAuth-Scopes einschließlich `offline_access`.

## Codex CLI und Desktop

```sh
codex plugin marketplace add https://github.com/matecode/mcp-marketplace.git
codex plugin add mail-mcp@mate-mcp
codex mcp list
```

Alternativ mit SSH:

```sh
codex plugin marketplace add git@github.com:matecode/mcp-marketplace.git
```

Weitere Plugin-IDs einzeln installieren. Codex Desktop nach Konfigurationsänderungen neu starten und den Katalog unter Plugins öffnen. CLI-Installation und Desktop-Darstellung sind getrennte Prüfungen.

Für einen CLI-Login die benötigten Scopes ausdrücklich angeben (keine Tokens ausgeben):

```sh
codex mcp login mail --scopes openid,profile,email,offline_access,mailbox
codex mcp login calendar --scopes openid,profile,email,offline_access,mailbox
codex mcp login lizu --scopes openid,profile,email,offline_access,lizu
codex mcp login obsidian --scopes openid,profile,email,offline_access
codex mcp login kleinanzeigen --scopes openid,profile,email,offline_access
```

Bei schon separat eingerichteten MCPs zuerst bestehende Einträge prüfen, um doppelte Verbindungen und Namenskollisionen zu vermeiden. Keine bestehende Clientkonfiguration blind überschreiben.

## Andere Oberflächen und Grenzen

Claude Code ist der hier geprüfte Claude-Client. Für normales Claude Web/Desktop beziehungsweise Cowork ist die Plugin-/Connector-Verteilung separat zu prüfen; diese Anleitung behauptet dort keinen erfolgreichen Marketplace-Import. Bestehende Connector-Einrichtung über die jeweilige MCP-Adresse bleibt möglich.

Bei OpenAI sind lokale/Git-Marketplaces von der universellen öffentlichen Plugin Directory getrennt. Ein Workspace-Import gebündelter MCP-Dateien gilt laut OpenAI-Dokumentation als Desktop-only, auch mit HTTPS-Servern. Dieses Repository wurde nicht in eine öffentliche Directory eingereicht.

Installation allein bestätigt weder OAuth-Login noch Werkzeugfunktion, Refresh oder Datenisolation. Schreibwerkzeuge können vorhanden sein; das Paket erweitert keine serverseitige Freigabe und enthält keine lokale Allowlist. Gesprächsablage-Regeln bleiben im Obsidian-MCP und seiner zentralen Vault-Notiz; keine zusätzliche Skill-Kopie.

## Warum zwei unterschiedliche Marketplace-Dateien?

Claude Code verwendet `.claude-plugin/marketplace.json` mit `owner`, optionalen `metadata` und einem Plugin-Pfad als `source`-String. Der native Codex-Katalog unter `.agents/plugins/marketplace.json` verwendet hier ein `source`-Objekt sowie `interface.displayName`, `category` und `policy` für Installations-/Anmeldeverhalten.

Codex unterstützt auch das Claude-kompatible Marketplace-Format: Zwei Dateien sind deshalb keine zwingende Voraussetzung. Dieser Marketplace verwendet bewusst beide nativen Katalogformate, um Codex-spezifische Anzeige- und Policy-Felder ausdrücklich bereitzustellen. Beide Kataloge zeigen auf dieselben fünf Plugin-Verzeichnisse; die MCP-Adressen stehen gemeinsam in der jeweiligen `.mcp.json`. Der Offline-Prüfer kontrolliert die Übereinstimmung von Plugin-Namen und Pfaden sowie die vorgesehenen Policies.

## Pflege und Prüfung

Claude: `.claude-plugin/marketplace.json`. Codex: `.agents/plugins/marketplace.json`. Beide verweisen auf dieselben Verzeichnisse in `plugins/`. Je Plugin werden `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json` und `.mcp.json` gepflegt. Die nachweislich unterstützten Kompatibilitätsformate vermeiden hier eine zusätzliche portable Manifest-Kopie.

```sh
python3 scripts/check-marketplace.py
claude plugin validate . --strict
```

Bei Paketänderungen Version in beiden Plugin-Manifesten und im Claude-Katalog erhöhen; Katalogversion ebenfalls aktualisieren. Updates:

```sh
claude plugin marketplace update mate-mcp
claude plugin update mail-mcp@mate-mcp
codex plugin marketplace upgrade mate-mcp
codex plugin add mail-mcp@mate-mcp
```

Keine Secrets, Nutzdaten, internen NAS-Pfade oder Serverkonfigurationen übernehmen. Infrastrukturquellen bleiben in [homelab-infra](https://github.com/matecode/homelab-infra); übergreifendes Betriebswissen im privaten Homelab-Vault.

## Verifizierter Paketstand – 2026-10-16

- Claude Code 2.1.301: beide Katalog-/Paketprüfungen ohne Fehler oder Warnungen; alle fünf Plugins in einer isolierten temporären Konfiguration installiert. `plugin details` erkennt jeweils genau einen MCP-Server.
- Codex CLI 0.162.1: lokalen Marketplace registriert, alle fünf Plugins in einem isolierten temporären `CODEX_HOME` installiert. `codex mcp list --json` lädt alle fünf korrekten HTTPS-Adressen als Streamable HTTP.
- Keine persönliche Clientkonfiguration geändert; keine MCP-Werkzeuge aufgerufen und keine laufenden Server geändert.
- Noch offen: persönlicher OAuth-Login, tatsächliche Werkzeugaufrufe und Refresh aus installierten Plugins; Codex-Desktop-Anzeige und Claude-Web-/Cowork-Import.

Beim ursprünglichen Einrichtungsstand bestätigte die GitHub-API `PRIVATE` und Hauptbranch `main`. Beide Clients haben das private Repository über SSH mit unveränderter Hostschlüsselprüfung abgerufen und das Mail-Plugin aus dem Remote-Katalog installiert. Claude erkennt den Mail-MCP; Codex lädt die korrekte Mail-Adresse und meldet `not_logged_in`. Dies bestätigt Remote-Installation, keinen OAuth-Login. Quelle: GitHub-API und isolierte CLI-Prüfungen am 2026-10-16.

## Quellen

- [OpenAI: Paketierung und Marketplace](https://developers.openai.com/plugins/build/plugins)
- [OpenAI: GitHub-Import und private Repositories](https://developers.openai.com/codex/enterprise/plugin-management)
- [Claude: Marketplace erstellen](https://code.claude.com/docs/en/plugins/create-marketplace)
- [Claude: private Marketplace-Zugriffe](https://code.claude.com/docs/en/plugins/host-marketplace)
- [Claude: MCP-Komponenten](https://code.claude.com/docs/en/plugins/components#mcp-servers)

## Öffentliche Freigabe – 2026-10-17

Auf ausdrücklichen Nutzerauftrag auf öffentlich umgestellt. GitHub-API bestätigt `PUBLIC`; eine zusätzliche anonyme HTTPS-Anfrage ohne Zugangsdaten bestätigt `private=false`. Das Infrastruktur-Repository `matecode/homelab-infra` bleibt `PRIVATE`. Quelle: authentifizierte GitHub-Abfrage und anonymer API-Abruf am 2026-10-17, 03:03 CEST. Vollständige bisherige Marketplace-Git-Historie auf Schlüssel-/Tokenmuster und interne IP-/NAS-/lokale Pfade geprüft, keine Treffer; keine Actions-Läufe vorhanden.

Anonymer Git-Abruf über HTTPS scheiterte bei dieser Prüfung an einem Verbindungstimeout; kein erneuter Client-Installationstest nach der Sichtbarkeitsänderung. Persönliche MCP-Anmeldung und Dienstfreigaben sind weiterhin erforderlich. Keine laufenden MCP-Dienste oder persönlichen Client-Einstellungen geändert.
