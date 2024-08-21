import logging
from mysql.connector import Error
import mysql.connector

def setup_database(file, connection):
    with open(file, 'r') as file:
        sql = file.read()

    cursor = connection.cursor()

    try:
        cursor.execute(sql, multi=True)  # `multi=True` erlaubt das Ausführen mehrerer SQL-Befehle
        connection.commit()
    except Error as e: logging.error(f"Error: {e}")
    finally:
        cursor.close()

def main():

    try:
        #Check for the right stats
        connection = mysql.connector.connect(
            user = 'philipp',
            password = '1234',
            host = 'localhost', 
            database = 'onlineshop',
            collation='utf8mb4_unicode_ci'
        )
        logging.info("Database connection established")

        #SQL Dateien einlesen und Datenbanke erstellen
        #Only execute if Database is not filled
        setup_database("create_database.sql", connection)
        #setup_database("fill_database.sql", connection)

        #cursor = connection.cursor()
        #cursor.execute('SELECT * FROM product')
        #rows = cursor.fetchall()
#
        #for tuple in rows:
        #    quant = int(tuple[2])
        #    print(quant)


    except Error as e: logging.error(f"Error: {e}")

    finally:
        if connection.is_connected():
            connection.close() 

if __name__ == "__main__":
    main()