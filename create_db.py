import sqlite3

conn = sqlite3.connect('dalton.db')
cursor = conn.cursor()

sql = '''
CREATE TABLE Student (
    student_id TEXT PRIMARY KEY, 
    student_name TEXT,
    roll_no INTEGER, 
    stream TEXT, 
    academic_year_from INTEGER,
    academic_year_to INTEGER
)
'''

cursor.execute(sql)
conn.commit()
conn.close()
