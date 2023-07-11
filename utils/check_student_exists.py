import sqlite3

def check_student_exists(db,table_name, student_id):
    """
    This function takes table_name and student_id as the parameters
    and checks if the given student_id exists in the table .
    """
    cursor = db.cursor()
    sql = f"SELECT 1 FROM {table_name} WHERE student_id = ?"
    cursor.execute(sql, (student_id,))
    row = cursor.fetchone()
    if row is not None:
        return True
    else:
        return False
