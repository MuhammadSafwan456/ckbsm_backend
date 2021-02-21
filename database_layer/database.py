import mysql.connector
import pymysql
from config.database_config import DB_NAME, DB_HOST, DB_PASSWORD, DB_USERNAME
from constants.database_constants import NO_CONNECTION, NO_CURSOR

my_db = NO_CONNECTION
my_cursor = NO_CURSOR


def use_database_query():
    """
    generate query to use database
    """
    return "USE " + DB_NAME


def make_connection():
    """"
    make connection to database & use that database
    """
    global my_db, my_cursor
    # my_db = mysql.connector.connect(host=DB_HOST, user=DB_USERNAME, password=DB_PASSWORD)
    my_db = pymysql.connect(host=DB_HOST, user=DB_USERNAME, password=DB_PASSWORD,
                            cursorclass=pymysql.cursors.DictCursor, autocommit=True)
    my_cursor = my_db.cursor()
    query = use_database_query()
    select_query(query)


def select_query(query):
    """
    execute the query & return the cursor
    """
    if my_db == NO_CONNECTION:
        make_connection()

    my_cursor.execute(query)
    return my_cursor


def insert_query(query):
    """
    execute the query & return the cursor
    """
    if my_db == NO_CONNECTION:
        make_connection()
    try:
        my_cursor.execute(query)
    except:
        return False
    if my_cursor.rowcount > 0:
        return True
    return False
