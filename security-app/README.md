https://www.python.org/downloads/windows/ -> download & run python-3.14.2-amd64.exe 
Settings -> Virus & Threat protection -> Ransomware protection -> Controlled folder access off

> python -m venv venv - kreirali smo virtual environment (izolovano Python okruženje u kojem projekat koristi sopstvene biblioteke i verzije, nezavisno od ostatka sistema)

> venv\Scripts\Activate.ps1 - aktiviramo virtual environment!!!

(venv)> pip install bcrypt - instaliramo biblioteku za hešovanje lozinki

db.py - Definiše se konekcija ka lokalnoj bazi users.db, a zatim se kreira tabela users ukoliko već ne postoji. Tabela čuva podatke o korisnicima, uključujući korisničko ime i hešovanu lozinku. Na kraju se promene čuvaju i konekcija zatvara, a skripta se pokreće samo jednom kako bi pripremila bazu za rad aplikacije.

(venv)> python db.py - inicijalizujemo SQLite bazu i kreiramo tabelu za korisnike

Nakon inicijalizacije baze, implementirana je autentikaciona logika koja omogućava registraciju i prijavu korisnika uz bezbedno čuvanje lozinki.

auth.py - Ovaj fajl sadrži logiku za registraciju i prijavu korisnika. Lozinke se pre čuvanja hešuju pomoću bcrypt biblioteke, a prilikom prijave se porede heš vrednosti. Podaci se čitaju i upisuju u SQLite bazu korišćenjem parametrizovanih SQL upita, čime se sprečava SQL injection.

Test autentikacije (bez GUI-ja) 

(venv)> python - pokrećemo Python interpreter radi testiranja autentikacione logike

>>> from auth import register_user, login_user
>>> register_user("test", "test123")
>>> login_user("test", "test123")

Program vraća True 

app.py - Implementira grafički korisnički interfejs pomoću Tkinter biblioteke i povezuje GUI sa autentikacionom logikom aplikacije.

(venv)> python app.py - Pokrećemo GUI

==============================================================================================
#                                            TEST                                            #
==============================================================================================

Pokrenuti aplikaciju tako što ćete uneti sledeće komande u terminal: 

> venv\Scripts\Activate.ps1
(venv)> python app.py

Nakon što se prikazalo grafičko okruženje izaberite opciju da se ulogujete ili registrujete.
Registracija prikazuje jačinu lozinke i proverava da li su unete lozinke međusobno podudarne.

Nakon što napravite nalog možete se ulogovati tako što ćete uneti korisničko ime i lozinku.
Ukoliko odaberete dugme "DEMO" osposobićete poseban DEMO režim koji služi isključivo za edukativnu demonstraciju SQL Injection napada.

Secure mode – koristi parametrizovane SQL upite (bezbedno).
Demo mode – koristi nebezbedno konkateniranje SQL upita (ranjivo).

U polje Username uneti jedan od sledećih SQL injection payload-a:

' OR '1'='1
' OR 1=1 --

Polje Password može sadržati bilo koju vrednost.
Kliknuti LOGIN i prijava će uspeti bez validnih kredencijala.

!!! Ukoliko se korisnik uspešno ulogovao ima opciju da preuzme bazu podataka
* Baza podataka ce se koristiti u sledećoj C# aplikaciji