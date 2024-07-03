#Python code to save info back to original database
import sqlite3
from urllib.request import pathname2url
from sqlite3 import Error

try:
    conn = sqlite3.connect('info.db')
    cursor = conn.cursor()
    db = cursor.execute("""SELECT link FROM Link""").fetchone()[0]
    dburi = 'file:{}?mode=rw'.format(pathname2url(db))
    o_conn = sqlite3.connect(dburi, uri=True)
    o_cursor = o_conn.cursor()
except sqlite3.OperationalError:
        print('Error: Database does not exist')
        print('Program terminated.')
        input()
        exit()
except Error as e:
    print(e)

o_cursor.execute("ATTACH DATABASE '{}' AS db".format(pathname2url('info.db')))
for student in cursor.execute("""SELECT * FROM Stdntinfo;""").fetchall():
    if student[0] in [s[0] for s in cursor.execute("""SELECT stdntid FROM stdntevents;""").fetchall()]:
        for event in cursor.execute("""SELECT event FROM Events 
                                       JOIN stdntevents ON Events.id = stdntevents.eventid
                                       JOIN Stdntinfo ON Stdntinfo.id = stdntevents.stdntid
                                       WHERE Stdntinfo.id = ?;""", (student[0],)):
            table = ' '.join((student[8], student[6].split('#')[1],)).replace(' ', '_')
            print(event)
            eventname = '_'.join((student[6].split('#')[1], event[0],)).replace(' ', '_')
            print(table)
            print(eventname)
            print(student[1])
            query="""UPDATE {} SET {} = 1 WHERE id = "{}";""".format(table, eventname, student[1])
            print(query)
            o_cursor.execute(query)
o_conn.commit()