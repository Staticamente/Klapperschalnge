Klapperschlange – README
Übersicht
Klapperschlange ist ein grid‑basiertes Musiksystem, das von der Spielmechanik von „Snake“ inspiriert ist.
Schlangen bewegen sich über ein zweidimensionales Raster und lösen dabei Noten, Drum‑Samples und Steuerbefehle aus.
Über verschiedene Modi können musikalische Strukturen wie Loops, Melodien und rhythmische Patterns erstellt werden.

Start des Programms
Programm starten (z.B. python main.py oder entsprechendem Skriptnamen).

Nach dem Start erscheint das Hauptfenster mit:

einem Raster (Spielfeld) für die Schlangen

einer rechten Seitenleiste mit Erklärung der Befehle und Tastenkombinationen

Modi und Steuerung
Die Arbeit im Programm erfolgt über Modi, in denen unterschiedliche Blocktypen auf das Raster gesetzt werden.
Die Modi werden über Tastenkombinationen gewechselt (siehe rechte Seite des GUIs).

Note‑Modus (N)

Aktivieren: Note‑Modus auswählen (z.B. Taste N, je nach Implementierung).

Im Note‑Modus platzierst du Tonhöhen auf dem Raster.

Die Noten sind als Zahlen 1 bis 9 codiert und bilden neun Stufen der C‑Dur‑Tonleiter.

Wenn eine Schlange ein Feld mit einer Note betritt, wird die entsprechende Note abgespielt.

Zusätzlich gibt es Drum‑Samples:

Kick: Taste Z

Snare: Taste X

Hi‑Hat: Taste C

Platziere diese Felder auf dem Raster; beim Betreten durch eine Schlange wird der passende Drum‑Sound ausgelöst.

So kannst du melodische Linien und Drum‑Loops erstellen.

Turn‑Modus (T)

Aktivieren: Turn‑Modus auswählen (z.B. Taste T).

Im Turn‑Modus setzt du Richtungsblöcke, die die Bewegungsrichtung einer Schlange ändern.

Mögliche Richtungen: oben, unten, links, rechts.

Durch geschickte Platzierung kannst du:

Schleifen/Loops erzeugen

komplexe Bewegungsmuster bauen

Dadurch entstehen periodische Sequenzen, die sich automatisch wiederholen.

Snake‑Modus (S)

Aktivieren: Snake‑Modus auswählen (z.B. Taste S).

Im Snake‑Modus platzierst du neue Schlangen auf dem Raster.

Nach dem Start bewegen sich die Schlangen automatisch in eine voreingestellte Richtung.

Wenn du eine Schlange direkt auf einem Turn‑Block platzierst, wird ihre Start‑Richtung durch diesen Block festgelegt.

Du kannst mehrere Schlangen gleichzeitig setzen; sie bewegen sich unabhängig und können so parallele musikalische Ereignisse erzeugen.

Delete‑Modus

Aktivieren: Delete‑Modus auswählen (z.B. eigene Taste, etwa D).

Im Delete‑Modus können bereits gesetzte Blöcke (Noten, Drum‑Samples, Turn‑Blöcke, Pause‑Blöcke, etc.) wieder entfernt werden.

Damit kannst du Sequenzen nachträglich korrigieren oder neu gestalten.

Weitere Funktionen / Effekte

Pause‑Block (P):

Wird über den Effekt‑Modus (E) gesetzt (z.B. E für Effekt‑Modus, dann P für Pause‑Block).

Wenn eine Schlange diesen Block passiert, entsteht eine kurze Pause im musikalischen Ablauf.

Das System ist erweiterbar, z.B. um Effekte wie Reverb oder Low‑Pass‑Filter (derzeit konzeptionell vorgesehen, aber noch nicht umgesetzt).

Layout und Spielfeldlogik
Das Spielfeld ist ein zweidimensionales Raster.

Die Schlangen bewegen sich kontinuierlich über dieses Raster.

Wenn eine Schlange den Rand des Rasters verlässt, erscheint sie auf der gegenüberliegenden Seite wieder (Wrap‑Around wie im klassischen „Snake“).

Rechts im GUI:

Kurze Beschreibung der vorhandenen Blöcke

Übersicht der Tastenkombinationen für die Modi

Typischer Workflow
Programm starten.

Snake‑Modus aktivieren und eine oder mehrere Schlangen auf das Raster setzen.

Turn‑Modus auswählen und die Bewegungsbahn der Schlangen mit Turn‑Blöcken gestalten (Loops bauen).

Note‑Modus aktivieren und entlang der Bahn Noten (1–9) und Drum‑Samples (Z/X/C) platzieren.

Optional: Effekt‑Modus nutzen und Pause‑Blöcke (P) setzen.

Sequenz abspielen lassen und bei Bedarf im Delete‑Modus Blöcke entfernen und neu arrangieren.

Lizenz
Dieses Projekt ist unter der MIT‑Lizenz veröffentlicht.
Details siehe die Datei LICENSE im Repository.

