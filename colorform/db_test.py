import os
import struct
import pyodbc
from azure.identity import ManagedIdentityCredential

SQL_SERVER = os.environ["SQL_SERVER"]
SQL_DATABASE = os.environ["SQL_DATABASE"]
MI_CLIENT_ID = os.environ["MI_CLIENT_ID"]

cred = ManagedIdentityCredential(client_id=MI_CLIENT_ID)
token = cred.get_token("https://database.windows.net/.default").token

# ODBC expects an ACCESSTOKEN struct: 4-byte length + UTF-16-LE token bytes
token_bytes = token.encode("utf-16-le")
token_struct = struct.pack("<I", len(token_bytes)) + token_bytes

conn_str = (
    "Driver={ODBC Driver 18 for SQL Server};"
    f"Server=tcp:{SQL_SERVER},1433;"
    f"Database={SQL_DATABASE};"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
    "Connection Timeout=30;"
)

print("Connecting to:", SQL_SERVER, "DB:", SQL_DATABASE)

cn = pyodbc.connect(conn_str, attrs_before={1256: token_struct})
cur = cn.cursor()
cur.execute("SELECT SUSER_SNAME(), DB_NAME()")
print("Connected as:", cur.fetchone())
cn.close()
print("SUCCESS")
