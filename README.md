# Generator izvoda za Raiffeisen banku #

Aplikacija cita e-mail-ove i preuzima priloge koji su u XML formatu. 
Iz njih izvlaci podatke i pakuje ih u jedan CSV fajl koji moze nakon toga da se obradjuje u Excell-u.

# Priprema okruzenja #

Potrebno je instalirati Python verziju 3.10.7 ili vecu. Prilikom instalacije obavezno instalirati PIP. 
Na Windowsu bi trebalo da je to "default" opcija.

        https://www.python.org/downloads/windows/


Nakon ovoga otvoriti python konzolu iz start menija i pokrenuti komandu:

        pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

Ovo ce instalirati potrebne biblioteke za citanje e-mail-ova.

# Pokretanje aplikacije #

Pre pokretanja skripta, potrebno je podesiti konfiguraciju u fajlu: config.py
Tu mogu da se podese datumi za koje je potrebno generisati izvod.

Skript koji treba pokrenuti je: raiffeisen_report.py
Na Windows-u, ako si prilikom instalacije izabrao da registruje Python na sistem, trebalo bi dvoklik na skript da ga pokrene.
Ako nije registrovan Python, potrebno je otvoriti Python konzolu, navigirati u ovaj folder i otkucati:

        python raiffeisen_report.py

Pri prvom pokretanju ce se otvoriti web browser kako bi se autorizovala aplikacija za citanje mail-a. 
Naravno, potrebno je odabrati GMAIL nalog na koji stizu Raiffeisen izvodi.

# Napomena #

Potrebno je da ja odobrim nalog za koristenje u mojoj developer konzoli, pa ako te Google odbije, javi mi da dodam tvoju adresu na moj "developers.google.com" nalog.



