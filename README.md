
# Dies ist ein Bewertungsportal für  Restaurants in Hamburg


## Features ##

- [x] Login/Logout
- [x] Registrierung
- [x] Bewertung
- [x] Kommentare
- [x] Detailansicht
- [x] Suchfunktion
- [x] Kategoriesierung
- [x] Mittelwert jeweiliger Bewertungen
- [x] Top 5

## Hinweise zur Installation / Ausführung

Nach dem Entpacken des Archives ist keine weitere Installation der Anwendung notwendig. Zur Einrichtung und Ausführung wird allerdings Python 2.7 und pip benötigt.

Danach werden folgende Befehle in einer Konsole nacheinander ausgeführt:

1. Mittels~cd<pfad>in den Installationsordner navigieren
2. Falls das Flask Frame work noch nicht installiert ist
a. ~ pip install flask und warten bis Flask installiert ist
3. Falls das Flask Framework bereits installiert ist
a. ~ pip install flask --upgrade um sicherzustellen, dass die Version aktuell ist
4. Nun muss Flask in einer Umgebungsvariable mitgeteilt werden, welche Anwendung ausgeführt werden soll: ~ export FLASK_APP=application.py Hierbei ist es wichtig, dass die Konsole im gleichen Ordner, wie die Datei application.py ist.
5. Im letzten Schritt muss der Server nun gestartet werden. Je nach Installationsumgebung reicht der Befehl ~ flask run dafür aus, sicher funktioniert jedoch ~ python -m flask run.
6. Wenn alles geklapp that,sollte in der Konsole folgender Text bestätigen,dass der Server läuft:
* Serving Flask app “application” 
* Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
7. Nun kann die Anwendung in einem beliebigen Browser unter der Adressse http://127.0.0.1:5000/ aufgerufen werden.
8. Wer die Registrierung überspringen möchte kann sich mit dem Benutzernamen Tester und dem Passwort 123 anmelden.
9. Viel Spaß mit der Anwendung!
