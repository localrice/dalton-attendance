import sqlite3

#cursor = conn.cursor()
DATABASE = 'dalton.db'
db = sqlite3.connect(DATABASE)
cursor = db.cursor()
def check_student_exists(table_name, student_id):
    """
    This function takes table_name and student_id as the parameters
    and checks if the given student_id exists in the table .
    """
    sql = f"SELECT 1 FROM {table_name} WHERE student_id = ?"
    cursor.execute(sql, (student_id,))
    row = cursor.fetchone()
    if row is not None:
        return True
    else:
        return False
