https://www.python.org/downloads/windows/ -> download & run python-3.14.2-amd64.exe 
Settings -> Virus & Threat protection -> Ransomware protection -> Controlled folder access off
python -m venv venv - kreirali smo virtual environment (izolovano Python okruženje u kojem projekat koristi sopstvene biblioteke i verzije, nezavisno od ostatka sistema)
> venv\Scripts\Activate.ps1 - aktiviramo virtual environment
pip install bcrypt - instaliramo biblioteku za hešovanje lozinki

db.py - Definiše se konekcija ka lokalnoj bazi users.db, a zatim se kreira tabela users ukoliko već ne postoji. Tabela čuva podatke o korisnicima, uključujući korisničko ime i hešovanu lozinku. Na kraju se promene čuvaju i konekcija zatvara, a skripta se pokreće samo jednom kako bi pripremila bazu za rad aplikacije.

(venv)> python db.py - inicijalizujemo SQLite bazu i kreiramo tabelu za korisnike