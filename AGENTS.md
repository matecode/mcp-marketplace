# Mate MCP Marketplace

## MCP-Clienteinrichtung – Nutzerentscheidung, 2026-11-03

Mate richtet MCPs künftig selbst in seinen Clients ein: Plugin-/Connectorinstallation, Anmeldung und Zustimmung übernimmt er. Bei neuen MCPs Server, Marketplace-Paket und vollständige Einrichtungsanleitung liefern; keine Clientkonfiguration ändern oder OAuth-Browserlogins starten, auch nicht als automatische Clientabnahme. Offline-Paketvalidierung und serverseitige Lese-/Authentifizierungsprüfungen bleiben Teil der Umsetzung. Tatsächliche Clientnutzung/Refresh nur nach belegter Nutzerbestätigung oder einem neuen ausdrücklichen Prüfauftrag dokumentieren. Für Fileee ist Claude Web/App der gewünschte Client; Einrichtung durch Mate.

Öffentlicher Plugin-Katalog `matecode/mcp-marketplace`, Marketplace-ID `mate-mcp`. Deutsch.

Plugin-Metadaten, MCP-Verbindungsdaten, technische Installationshinweise sowie den ausdrücklich beauftragten offiziellen HA-Best-Practice-Skill pflegen. Keine Secrets, Nutzdaten, Vault-Inhalte oder Serverkonfigurationen übernehmen. Repository-Zugriff und persönliche Dienstfreigabe sind unabhängig. Änderungen hier erteilen keine Freigabe für NAS-Deployments.

Claude-Katalog: `.claude-plugin/marketplace.json`; Codex-Katalog: `.agents/plugins/marketplace.json`. Gemeinsame Plugins unter `plugins/`, je Plugin Claude-/Codex-Manifest und `.mcp.json`. Fileee verwendet zusätzlich `mcp.codex.json` mit nativem `oauth.client_id`, `callback_port` und Scope-Liste für die geprüfte Codex-CLI-Version; Codex-Manifest darauf verweisen lassen. Namen, Versionen, Pfade, OAuth-Scopes und URLs konsistent halten. Keine lokale Werkzeug-Allowlist oder zusätzliche Gesprächsablage-Skills hinzufügen.

Prüfen: `python3 scripts/check-marketplace.py` und `claude plugin validate . --strict`. Clientinstallation und OAuth-Anmeldung übernimmt Mate; weitergehende Clienttests nur auf neuen ausdrücklichen Auftrag und mit isolierten temporären Konfigurationsverzeichnissen. OAuth, Werkzeugfunktion und Refresh getrennt von Paketprüfungen dokumentieren. Keine Schreibproben an Mail, Kalender, Anzeigen oder Vault ohne konkreten Auftrag.

Übergreifendes Betriebswissen im Homelab-Vault; Infrastrukturquellen in `matecode/homelab-infra`.

Fileee ist das siebte Plugin. Native Authentik-Anbindung mit öffentlicher Client-ID `fileee-mcp`, PKCE und ohne Clientsecret; keine DCR. Claude Code `oauth.clientId`, Codex `oauth.client_id`. Scopes `openid profile email offline_access fileee`. Codex CLI 0.163.0-alpha.10.2 übernimmt das portable Auth-Feld aus Paket 0.1.0 nicht; ab 0.1.1 verwendetes natives Format startet den richtigen PKCE-Login. Bei Clientupdates Paketformat erneut prüfen; Dokumentationsschema allein genügt nicht als Kompatibilitätsnachweis. Eigene dienstseitige Konto-/Freigabezuordnung nötig; keine Zugangsdaten oder internen Secretnavigationslinks im öffentlichen Paket. Claude Web/App wird über den Remote-Connector gesondert eingerichtet. Paketvalidierung, echter Clientlogin, Fileee-Funktion und Refresh getrennt dokumentieren.

Öffentliche Git-Historie mitprüfen; niemals Geheimnisse oder interne Betriebsdetails aufnehmen. Anonymes HTTPS ist der Standard-Installationsweg. Änderungen der Repository-Sichtbarkeit nur auf ausdrücklichen Nutzerauftrag.

Home Assistant ist das sechste Plugin: ab 0.3.0 stabile öffentliche MCP-Adresse mit Original-HA-Apps und HA-OAuth, ohne Authentik-Scopes oder persönliche OpenBao-HA-Tokenvermittlung. Client-ID/Client-Secret/Scopes leer; bei Codex nötigenfalls `--oauth-client-registration dcr`. Werkzeugrechte folgen dem HA-Zugang der Server-App. Keine interne HA-Adresse oder Webhook-Geheimnisse in den Katalog aufnehmen. Die Aufnahme in beide Marketplace-Kataloge ist keine Installation in Claude Web.

Der Nutzer hat den im Video empfohlenen offiziellen `home-assistant-best-practices`-Skill zur Bündelung im Home-Assistant-Plugin beauftragt. Original und 15 Referenzen unverändert, MIT-Lizenz erhalten; Quelle/Version/Commit/Dateihashes in `plugins/homeassistant-mcp/upstream-skill.json`. Nur geprüfte gepinnte Updates veröffentlichen, keine globalen persönlichen Client-Skills installieren. `skills/` im Plugin-Root für beide Clients; Installation und tatsächliche Skill-Erkennung getrennt prüfen. Keine zusätzlichen Ablage-Skills oder lokale Werkzeug-Allowlist daraus ableiten.
