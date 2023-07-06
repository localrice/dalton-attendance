from flask import render_template, request, Flask, g
import sqlite3

#cursor = conn.cursor()
DATABASE = 'dalton.db'
app = Flask(__name__)

def get_initials(string):
    words = string.split()
    initials = [word[0].upper() for word in words]
    return ''.join(initials)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def check_student_exists(table_name, student_id):
    db = get_db()
    cursor = db.cursor()

    sql = f"SELECT 1 FROM {table_name} WHERE student_id = ?"
    cursor.execute(sql, (student_id,))
    row = cursor.fetchone()
    if row is not None:
        return True
    else:
        return False

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('index.html')


@app.route('/attendance', methods=['GET', 'POST'])
def attendance():
    if request.method == 'POST':
        selected_names = request.form.getlist('name')
        print(selected_names)
    names = ['kevi', 'hated', 'duck', 'neva']

    return render_template('attendance.html', names=names)


@app.route('/addStudents')
def add_students():
    return render_template('add_students.html')


@app.route('/data/', methods=['POST', 'GET'])
def data():
    db = get_db()
    cursor = db.cursor()
    if request.method == 'GET':
        return f"The URL /data is accessed directly. Try going to '/form' to submit form"
    elif request.method == 'POST':
        form_data = dict(request.form)  # form data from /addStudents
        
        stream_initials = get_initials(form_data.get('stream').title())
        name_initials = get_initials(form_data.get('student name'))
        student_id = stream_initials + name_initials + form_data.get('year1') + form_data.get('year2') + form_data.get('roll number')
        # if student_id doesn't exist yet, creates a column with the given data
        if check_student_exists(table_name='studentInfo',student_id=student_id) == False:
            sql_insert = "INSERT INTO studentInfo (student_id, student_name, roll_no, stream, academic_year_from, academic_year_to) VALUES (?, ?, ?, ?, ?, ?)"
            data = (student_id, form_data.get('student name'), int(form_data.get('roll number')), form_data.get('stream'),int(form_data.get('year1')), int(form_data.get('year2')))
            cursor.execute(sql_insert, data)
            db.commit()
        else:
            return render_template('student_already_exists.html')
        # check if the data is successfully saved
        status = check_student_exists(table_name='studentInfo',student_id=student_id)
        return render_template('data.html', form_data=form_data, status=status)


if __name__ == '__main__':
    app.run(debug=True)