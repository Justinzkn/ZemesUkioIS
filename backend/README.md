# Backend setup (Django)

Quick steps to prepare the development environment and connect to the remote MySQL/MariaDB database.

1) Activate the existing repository virtual environment (PowerShell). The repo already
	contains a venv at `C:\Users\justi\Downloads\ZemesUkioIS\venv` so use that:

```powershell
cd 'C:\Users\justi\Downloads\ZemesUkioIS'
.\venv\Scripts\Activate.ps1
cd backend
python -m pip install --upgrade pip
```

2) Install dependencies into the activated venv:

```powershell
pip install -r requirements.txt
```

3) Set DB connection environment variables in the same PowerShell session (examples):

```powershell
$env:DB_HOST = 'stud.if.ktu.lt'
$env:DB_PORT = '20001'
$env:DB_NAME = 'juskon2'
$env:DB_USER = 'juskon2'
$env:DB_PASSWORD = 'ooc0VohY4da5uquo'
```

Notes:
- To connect from inside the KTU network (or the server), use host `10.2.3.22` and port `3306`.
- From home you must be on the KTU VPN.
- If you prefer the `mysqlclient` C extension for better performance in production, install it instead of PyMySQL and remove the PyMySQL shim in `projektas/__init__.py`.

4) Run Django checks and migrations:

```powershell
python manage.py check
python manage.py migrate
python manage.py runserver
```

If `python manage.py check` reports `ModuleNotFoundError: No module named 'django'`, re-check that you installed the packages in the activated virtual environment.
