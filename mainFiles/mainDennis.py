import mysql.connector
from mysql.connector import Error
import logging

def execute_sql_file(file_path, host, user, password, database):
    connection = None
    cursor = None
    try:
        # Verbindung zur MySQL-Datenbank herstellen
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4',  # Charset festlegen
            collation='utf8mb4_general_ci'  # Collation explizit festlegen
        )

        # Cursor-Objekt erstellen, um SQL-Anweisungen auszuführen
        cursor = connection.cursor()

        # SQL-Datei einlesen
        with open(file_path, 'r', encoding='utf-8') as file:
            sql_script = file.read()

        # SQL-Skript ausführen
        for statement in sql_script.split(';'):
            if statement.strip():  # Verhindert das Ausführen leerer Statements
                cursor.execute(statement)

        # Änderungen in der Datenbank speichern
        connection.commit()
        print("SQL-Skript wurde erfolgreich ausgeführt.")

    except mysql.connector.Error as err:
        print(f"Fehler: {err}")
        if connection:
            connection.rollback()

    finally:
        # Verbindung schließen
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# create tables
execute_sql_file(
    file_path='sqlFiles/create_database.sql',  # Pfad zur SQL-Datei
    host='localhost',               # MySQL-Server-Adresse
    user='dennis',       # MySQL-Benutzername
    password='füller',       # MySQL-Passwort
    database='marktplatz'      # Name der Datenbank
)


# fill tables with values
execute_sql_file(
    file_path='sqlFiles/fill_database.sql',  # Pfad zur SQL-Datei
    host='localhost',             # MySQL-Server-Adresse
    user='dennis',     # MySQL-Benutzername
    password='füller',     # MySQL-Passwort
    database='marktplatz'    # Name der Datenbank
)
