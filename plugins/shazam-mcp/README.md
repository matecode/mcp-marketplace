# Shazam MCP

Eigene importierte Shazam-Titel lesen und durchsuchen, weitere Datenexporte anfordern sowie Tags, Notizen, Favoriten und Archiv lokal verwalten. Öffentliche MCP-Adresse: **https://mcp.bunteban.de/shazam/mcp**. Version 0.1.0.

## Persönliche Einrichtung

1. [Shazam einrichten](https://mcp.bunteban.de/shazam/setup) öffnen und selbst bei Authentik anmelden. Eine Dienstfreigabe ist erforderlich.
2. Die E-Mail-Adresse des Android-Shazam-Kontos eingeben und die Bestätigungs-E-Mail anfordern. Das Linkziel aus dieser E-Mail in das geschützte Formular kopieren, bevor der Link geöffnet wird. Keine Bestätigungslinks oder Tokens in einen Chat kopieren. Der Server prüft die Kontozuordnung und speichert den erneuerbaren Zugang im persönlichen OpenBao-Bereich.
3. Dieses Plugin selbst installieren und bei Authentik anmelden. Scopes: `openid profile email offline_access shazam`. Der Server unterstützt die dynamische MCP-Clientregistrierung; im Client keine eigene Client-ID und kein Clientsecret eintragen.
4. `shazam_request_export` aufrufen. Shazam kann für die Zustellung bis zu 30 Tage benötigen. Der Werkzeugaufruf bestätigt den Auftrag beziehungsweise einen offenen oder unsicheren Zustand, nicht den Empfang der Datei.
5. Nach Erhalt der Datei `shazam_create_import_upload` aufrufen und die Originaldatei über den persönlichen 15-Minuten-Link hochladen. Mit `shazam_preview_import` prüfen und mit `shazam_commit_import` übernehmen.
6. Danach `shazam_list_tracks` oder `shazam_search_tracks` nutzen. Alten und neuen Beispieltitel sowie die Titelzahl mit der Android-App vergleichen. Einen erledigten Exportauftrag erst nach Zustellungsprüfung mit `shazam_resolve_export_request` lokal abschließen.

Aktuell unterstützt: UTF-8-CSV mit `Title,Artist` und optional `Index,TagTime,URL,TrackKey`; JSON-Titelliste beziehungsweise `tracks` mit `title,artist`; ZIP mit genau einer solchen Datendatei. Maximal 10 MiB Upload und 32 MiB entpackte Daten. Die tatsächliche Privacy-Exportstruktur muss am ersten echten Export bestätigt werden; abweichende Formate werden verständlich abgelehnt und gezielt ergänzt.

## Clientinstallation

```sh
claude plugin marketplace add https://github.com/matecode/mcp-marketplace.git
claude plugin install shazam-mcp@mate-mcp
```

Anschließend in einer neuen Claude-Code-Sitzung `/mcp` öffnen und selbst authentifizieren.

```sh
codex plugin marketplace add https://github.com/matecode/mcp-marketplace.git
codex plugin add shazam-mcp@mate-mcp
codex mcp login shazam --scopes openid,profile,email,offline_access,shazam
```

Im Desktop kann das Plugin über den Marketplace ausgewählt werden. Für Claude Web/App die MCP-Adresse als Remote-Connector verwenden und selbst anmelden. Marketplace-Paketprüfung und Serverprüfung sind keine persönliche Clientabnahme.

## Werkzeuge und Grenzen

`shazam_connection_status`, `shazam_request_export`, `shazam_export_status`, `shazam_resolve_export_request`, `shazam_create_import_upload`, `shazam_preview_import`, `shazam_commit_import`, `shazam_list_tracks`, `shazam_search_tracks`, `shazam_get_track`, `shazam_update_local_track` und `shazam_export_library`.

Der Bestand stammt aus importierten Exporten und zeigt seinen Quellenstand. Fehlende Erkennungszeitpunkte bleiben unbekannt. Wiederholte Importe erhalten lokale Angaben; fehlende Titel werden nicht automatisch gelöscht. Tags/Archivierung verändern die Daten dieses MCPs, nicht die native Shazam-App.

Exportanforderung, E-Mail-Zustellung und Import sind getrennte Schritte. Noch kein autonomer Postfachempfang oder regelmäßiger Zeitplan. Die Shazam-E-Mail-Schnittstellen stammen aus dem öffentlichen Websitecode und können sich ändern. Bei `unknown_result` oder `sending` zuerst die Zustellung prüfen, keine blinden Wiederholungen.

Prüfstand 16.11.2026: Paketvalidierung bestanden; persönliche Shazam-Anmeldung, realer Export, tatsächliches Exportformat, Vollständigkeit und Clientnutzung noch offen. Die serverseitige Bereitstellung und ihre Abnahme werden in der Infrastruktur-Dokumentation geführt.
