# Portfoilioarbeit - Dashboard
Daniel Bonath, Tim Schacht, Quirin Barth

Video: https://www.youtube.com/watch?v=ds3Kx37JR5g


---

## Implementierung

Daten von Bluesky mithilfe des atproto Packets automatisiert gesammelt.

Aktiendaten mit yfinance Packet gesammelt.

Daten aufbereitet und Sentimentanalyse pro Post durchgeführt.

Daten in Prophet eingeführt um eine Vorhersage zu treffen.


## Reflexion

Prophet eignet sich eher für langzeitigere Vorhersagen, aber gibt dennoch Stabile vorhersagen, vor allem in kürzeren Zeiträumen.

Mit mehr Zeit hätte man ein ganzes Sequenzielles-Neuronales-Netz auf den Daten trainieren können, wodurch möglicherweise mehr flexibilität vor allem für schnelle Änderungen geboten werden könnte.

Man hätte noch mehr Daten sammeln können, wobei jedoch Bluesky nur eine begrenzte Anzahl an API calls pro tag erlaubt, was das ganze nochmal Zeitlich hinausgezogen hätte.

Möglicherweise könnte man die Vorhersagekraft weiter stärken, indem man mehr als nur den Sentimentwert pro Post in die Vorhersage mit rein nimmt.

