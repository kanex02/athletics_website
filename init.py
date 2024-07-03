import sqlite3
from urllib.request import pathname2url
from sqlite3 import Error
import csv
from werkzeug.security import generate_password_hash

#Connect to zo-sports database
try:
    db = input("URL:     ")
    dburi = 'file:{}?mode=rw'.format(pathname2url(db))
    o_conn = sqlite3.connect(dburi, uri=True)
    o_cursor = o_conn.cursor()
    o_cursor.execute("SELECT stage FROM details")
    details = o_cursor.fetchone()
    print("Current status: {}".format(details[0]))
    if details[0] != "Entry - Events":
        raise Error("Error: The selected database is not ready \nPlease make sure the program is in the event entry stage.")
except sqlite3.OperationalError:
        print('Error: Database does not exist')
        print('Program terminated.')
        input()
        exit()
except Error as e:
        print(e)
        exit()

#Connect to database
try:
    conn = sqlite3.connect('info.db')
    cursor = conn.cursor()
    cursor.execute('SELECT SQLITE_VERSION()')
    data = cursor.fetchone()
    print('SQLite version:', data)
except Error as e:
    print(e)

#Define table creation
def create_table(conn, create_table_sql):
    try:
        cursor.execute(create_table_sql)
    except Error as e:
        print(e)

def setup():
    #Create tables
    sql_create_info_table = """CREATE TABLE IF NOT EXISTS "Stdntinfo" (
                               id INTEGER PRIMARY KEY AUTOINCREMENT, 
                               oid STRING, 
                               studentid INTEGER,
                               firstname STRING,
                               surname STRING,
                               dob STRING,
                               grade STRING, 
                               formclass STRING,
                               division STRING);"""
    
    sql_create_events_table = """CREATE TABLE IF NOT EXISTS "Events" (
                               id INTEGER PRIMARY KEY AUTOINCREMENT, 
                               event STRING);"""

    sql_create_grades_table = """CREATE TABLE IF NOT EXISTS "Grades" (
                                 id INTEGER PRIMARY KEY AUTOINCREMENT, 
                                 grade STRING);"""
    
    sql_create_eventgrades_table = """CREATE TABLE IF NOT EXISTS eventgrades (
                                 id INTEGER PRIMARY KEY AUTOINCREMENT, 
                                 gradeid STRING,
                                 eventid STRING);"""

    sql_create_stdntevents_table = """CREATE TABLE IF NOT EXISTS stdntevents (
                                 id INTEGER PRIMARY KEY AUTOINCREMENT, 
                                 stdntid STRING,
                                 eventid STRING);"""

    sql_create_admin_table = """CREATE TABLE IF NOT EXISTS "Admin" (
                                 id INTEGER PRIMARY KEY AUTOINCREMENT, 
                                 username STRING,
                                 password_hash STRING);"""

    sql_create_link_table = """CREATE TABLE IF NOT EXISTS "Link" (
                                link STRING);"""

    create_table(conn, sql_create_events_table)
    create_table(conn, sql_create_info_table)
    create_table(conn, sql_create_grades_table)
    create_table(conn, sql_create_eventgrades_table)
    create_table(conn, sql_create_admin_table)
    create_table(conn, sql_create_link_table)
    create_table(conn, sql_create_stdntevents_table)
    #Save path to database
    cursor.execute("""INSERT INTO Link VALUES(?);""", (db,))
    print(cursor.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='Admin'").fetchone()[0])
    #If there isn't currently a login, ask user to create one
    if cursor.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='Admin'").fetchone()[0]==1:
        if cursor.execute("SELECT count(*) FROM Admin").fetchone()[0]!=0:
            print('Admin login already exists')
        else:
            username = input("Choose a username for admin login:    ")
            password = generate_password_hash(input("Choose a password:    "), "sha256")
            cursor.execute("""INSERT OR IGNORE INTO Admin VALUES(1, ?, ?);""", (username, password))
            conn.commit()
    else:
        username = input("Choose a username for admin login:    ")
        password = generate_password_hash(input("Choose a password:    "), "sha256")
        cursor.execute("""INSERT OR IGNORE INTO Admin VALUES(1, ?, ?);""", (username, password))
        conn.commit()


def extract():
    #Get information from original database
    cursor.execute("ATTACH DATABASE '{}' AS og".format(pathname2url(db).replace('%20', ' ')))

    cursor.execute("""INSERT INTO Stdntinfo (oid, firstname, surname, grade, dob, division) 
                      SELECT id, firstname, surname, combined_grade, dob, type 
                      FROM og.individuals
                      WHERE NOT EXISTS (SELECT 1 FROM Stdntinfo WHERE oid = og.individuals.id);""")
    print(cursor.execute("""SELECT firstname FROM og.individuals WHERE surname = 'Wong'""").fetchall())
    cursor.execute("""INSERT INTO Events (event) SELECT DISTINCT contest FROM og.template_events
                      WHERE contest NOT IN (SELECT event FROM Events);""")
    
    cursor.execute("""INSERT INTO Grades (grade) SELECT DISTINCT title FROM og.template_grades
                      WHERE category == 'combined'""")
    
    cursor.execute("""INSERT INTO eventgrades (gradeid, eventid) SELECT Grades.id, Events.id AS event FROM Grades 
                      INNER JOIN og.template_events ON og.template_events.grade = Grades.grade
                      INNER JOIN Events ON Events.event = og.template_events.contest""")
    
    #Get formclass from csv
    print('Database updated. ')
    lst = input("List URL:     ")
    with open(lst, 'rt') as f:
        stdnt_data = csv.reader(f)
        formc = []
        for row in stdnt_data:
            formc.append([r for r in row])
        cursor.execute("SELECT * FROM Stdntinfo")
        people = cursor.fetchall()
        print(len(people))
        print(len(formc))
        #Compare data from database(person) against row in csv (x)
        for person in people:
            for x in formc:
                #First name check
                if person[3].split(' ')[0].lower() == x[0].split(' ')[0].lower():
                    
                    print("matchf")
                    #Last name check
                    if person[4].split(' ')[-1].lower() == x[0].split(' ')[-1].lower():
                        print("matchl")
                        #DOB check
                        if person[5].replace('/', '')[4:8]+person[5].replace('/', '')[2:4]+person[5].replace('/', '')[0:2] == x[1]:
                            print("matchd")
                            cursor.execute("UPDATE Stdntinfo SET formclass = ?, studentid = ? WHERE id = (?)", (x[4], x[5], person[0]))
    #Save data
    conn.commit()

#If the script is initialized directly, run the code
if __name__ == '__main__':
    setup()
    extract()