https://www.python.org/downloads/windows/ -> download & run python-3.14.2-amd64.exe 
Settings -> Virus & Threat protection -> Ransomware protection -> Controlled folder access off
python -m venv venv - kreirali smo virtual environment (izolovano Python okruženje u kojem projekat koristi sopstvene biblioteke i verzije, nezavisno od ostatka sistema)
venv\Scripts\Activate.ps1 - aktiviramo virtual environment
pip install bcrypt - instaliramo biblioteku za hešovanje lozinki