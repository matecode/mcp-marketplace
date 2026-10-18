# Mate MCP Marketplace

Öffentlicher Plugin-Katalog `matecode/mcp-marketplace`, Marketplace-ID `mate-mcp`. Deutsch.

Plugin-Metadaten, MCP-Verbindungsdaten, technische Installationshinweise sowie den ausdrücklich beauftragten offiziellen HA-Best-Practice-Skill pflegen. Keine Secrets, Nutzdaten, Vault-Inhalte oder Serverkonfigurationen übernehmen. Repository-Zugriff und persönliche Dienstfreigabe sind unabhängig. Änderungen hier erteilen keine Freigabe für NAS-Deployments.

Claude-Katalog: `.claude-plugin/marketplace.json`; Codex-Katalog: `.agents/plugins/marketplace.json`. Gemeinsame Plugins unter `plugins/`, je Plugin Claude-/Codex-Manifest und `.mcp.json`. Namen, Versionen, Pfade und URLs konsistent halten. Keine lokale Werkzeug-Allowlist oder zusätzliche Gesprächsablage-Skills hinzufügen.

Prüfen: `python3 scripts/check-marketplace.py` und `claude plugin validate . --strict`. Client-Laden/Installation mit isolierten temporären Konfigurationsverzeichnissen prüfen, ohne persönliche Clientkonfiguration zu verändern. OAuth, Werkzeugfunktion und Refresh getrennt von Paketprüfungen dokumentieren. Keine Schreibproben an Mail, Kalender, Anzeigen oder Vault ohne konkreten Auftrag.

Übergreifendes Betriebswissen im Homelab-Vault; Infrastrukturquellen in `matecode/homelab-infra`.

Öffentliche Git-Historie mitprüfen; niemals Geheimnisse oder interne Betriebsdetails aufnehmen. Anonymes HTTPS ist der Standard-Installationsweg. Änderungen der Repository-Sichtbarkeit nur auf ausdrücklichen Nutzerauftrag.

Home Assistant ist das sechste Plugin: ab 0.3.0 stabile öffentliche MCP-Adresse mit Original-HA-Apps und HA-OAuth, ohne Authentik-Scopes oder persönliche OpenBao-HA-Tokenvermittlung. Client-ID/Client-Secret/Scopes leer; bei Codex nötigenfalls `--oauth-client-registration dcr`. Werkzeugrechte folgen dem HA-Zugang der Server-App. Keine interne HA-Adresse oder Webhook-Geheimnisse in den Katalog aufnehmen. Die Aufnahme in beide Marketplace-Kataloge ist keine Installation in Claude Web.

Der Nutzer hat den im Video empfohlenen offiziellen `home-assistant-best-practices`-Skill zur Bündelung im Home-Assistant-Plugin beauftragt. Original und 15 Referenzen unverändert, MIT-Lizenz erhalten; Quelle/Version/Commit/Dateihashes in `plugins/homeassistant-mcp/upstream-skill.json`. Nur geprüfte gepinnte Updates veröffentlichen, keine globalen persönlichen Client-Skills installieren. `skills/` im Plugin-Root für beide Clients; Installation und tatsächliche Skill-Erkennung getrennt prüfen. Keine zusätzlichen Ablage-Skills oder lokale Werkzeug-Allowlist daraus ableiten.
