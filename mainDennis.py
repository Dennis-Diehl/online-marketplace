import logging
from mysql.connector import Error
import mysql.connector

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

# Beispielaufruf der Funktion
execute_sql_file(
    file_path='create_database.sql',  # Pfad zur SQL-Datei
    host='localhost',               # MySQL-Server-Adresse
    user='dennis',       # MySQL-Benutzername
    password='füller',       # MySQL-Passwort
    database='marktplatz'      # Name der Datenbank
)



import mysql.connector

def execute_sql_file(file_path, host, user, password, database):
    """
    Liest eine SQL-Datei ein und führt die darin enthaltenen SQL-Befehle aus,
    um vorhandene Tabellen mit Werten zu füllen.

    :param file_path: Pfad zur SQL-Datei, die ausgeführt werden soll.
    :param host: Hostname oder IP-Adresse des MySQL-Servers.
    :param user: MySQL-Benutzername.
    :param password: MySQL-Passwort.
    :param database: Name der Datenbank, auf der die SQL-Befehle ausgeführt werden sollen.
    """
    connection = None
    cursor = None
    try:
        # Verbindung zur MySQL-Datenbank herstellen
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4',
            collation='utf8mb4_general_ci'
        )

        # Cursor-Objekt erstellen
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
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# Beispielaufruf der Funktion
execute_sql_file(
    file_path='fill_database.sql',  # Pfad zur SQL-Datei
    host='localhost',             # MySQL-Server-Adresse
    user='dennis',     # MySQL-Benutzername
    password='füller',     # MySQL-Passwort
    database='marktplatz'    # Name der Datenbank
)
