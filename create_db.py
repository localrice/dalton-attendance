import sqlite3

conn = sqlite3.connect('dalton.db')
cursor = conn.cursor()

sql = '''
CREATE TABLE IF NOT EXISTS StudentInfo11 (
    student_id TEXT PRIMARY KEY, 
    student_name TEXT,
    roll_no INTEGER, 
    stream TEXT, 
    phone_numbers INTEGER,
    academic_year_from INTEGER,
    academic_year_to INTEGER
)
'''

cursor.execute(sql)
conn.commit()
sql = '''
CREATE TABLE IF NOT EXISTS StudentInfo12 (
    student_id TEXT PRIMARY KEY, 
    student_name TEXT,
    roll_no INTEGER, 
    stream TEXT, 
    phone_numbers INTEGER,
    academic_year_from INTEGER,
    academic_year_to INTEGER
)
'''

cursor.execute(sql)
conn.commit()
sql = '''
CREATE TABLE IF NOT EXISTS dailyAttendance (
    date TEXT,
    class INTEGER,
    stream TEXT,
    present TEXT,
    absent TEXT
)
'''

cursor.execute(sql)
conn.commit()
conn.close()
