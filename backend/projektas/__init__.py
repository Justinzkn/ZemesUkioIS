"""Project package initialization.

We install PyMySQL as MySQLdb adapter so Django can use a pure-Python
connector. This avoids platform-specific build problems with mysqlclient
on some Windows setups. If you prefer mysqlclient, you can skip this and
install that package instead.
"""
try:
	import pymysql
	pymysql.install_as_MySQLdb()
except Exception:
	# If PyMySQL is not installed yet, Django will raise an ImportError at runtime.
	# We intentionally swallow the import error here so the environment can be
	# prepared before running Django commands.
	pass
