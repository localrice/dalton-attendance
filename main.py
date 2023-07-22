from os import path, walk
from flask import render_template, request, Flask, g
import sqlite3
from datetime import datetime
from utils.check_student_exists import check_student_exists
from utils.id_generator import id_generator
from utils.extract_info import roll_number_from_id,remove_number_from_end
from utils.sort_dict import sort_dict_by_id
from utils.list_string import list_to_string
import json


# some configs
DEBUG = True
DATABASE = 'dalton.db'

app = Flask(__name__)

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

@app.route('/', methods=['GET', 'POST'])    
def home():
    return render_template('index.html')


@app.route('/attendance', methods=['GET', 'POST'])
def attendance():
    return render_template('attendance.html')

@app.route('/attendance/stream/<stream_name>',methods=['GET','POST'])
def stream(stream_name):
    db = get_db()
    cursor = db.cursor()

    cursor.execute('SELECT student_id FROM StudentInfo WHERE stream = ?', (stream_name,))
    results = cursor.fetchall()
    #stores all the id of the students present in the stream without the academic year at the end
    student_id = [result[0] for result in results]

    cursor.execute('SELECT student_name FROM StudentInfo WHERE stream = ?', (stream_name,))
    results = cursor.fetchall()
    student_names = [result[0] for result in results] #stores all the names of the students present in the stream

    # creates a dictionary with the key as student's id and value as student's name arranged in increasing order of the roll number in the student id
    student_info = sort_dict_by_id(dict(zip(student_id, student_names)))

    if request.method == 'POST':
        selected_id = list(request.form.to_dict().keys())
        absent_student_ids = list(set(selected_id) ^ set(student_id))
        date = datetime.now().date().strftime("%d-%m-%Y")
        sql_insert = "INSERT INTO dailyAttendance (date, present, absent) VALUES (?, ?, ?)"
        data = (date,list_to_string(selected_id),list_to_string(absent_student_ids))
        cursor.execute(sql_insert, data)
        db.commit()
        return render_template('attendance_taken.html', stream_name=stream_name, student_info=student_info,
                                present_students=selected_id,absent_students = absent_student_ids,
                                len=len,max=max,str=str)
    return render_template('stream_attendance.html',student_info=student_info,roll_number_from_id=roll_number_from_id)

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
        stream = form_data.get('stream')
        roll_no = form_data.get('roll number')
        student_name = form_data.get('student name')
        year1 = int(form_data.get('year1'))
        year2 = int(form_data.get('year2'))
        phone_numbers_str = request.form.get('phone_numbers')
        phone_numbers = phone_numbers_str.split(',') if phone_numbers_str else []

        student_id = id_generator(stream=stream, roll_number=roll_no, name=student_name, year1=year1, year2=year2)    
        # if student_id doesn't exist yet, creates a column with the given data
        is_student_found = check_student_exists(db=db,table_name='studentInfo',student_id=student_id)
        if is_student_found == False:
            sql_insert = "INSERT INTO studentInfo (student_id, student_name, roll_no, stream, phone_numbers, academic_year_from, academic_year_to) VALUES (?, ?, ?, ?, ?, ?, ?)"
            data = (student_id, form_data.get('student name'), int(roll_no), stream, list_to_string(phone_numbers), year1, year2)
            cursor.execute(sql_insert, data)
            db.commit()
        elif is_student_found == 1:
            return "Roll no., stream, and academic year matches with another student."
        else:
            return render_template('student_already_exists.html')
        # check if the data is successfully saved
        status = check_student_exists(db=db,table_name='studentInfo',student_id=student_id)
        return render_template('data.html', form_data=form_data, status=status)

@app.route('/api/attendance/<input_string>')
def attendance_list(input_string):
    if request.args.get('date') == 'today':
            date_param = datetime.now().strftime("%d-%m-%Y")
            print(date_param)
    else:
        date_param = request.args.get('date')
    db = get_db()
    cursor = db.cursor()
    cursor.execute(f'SELECT {input_string} FROM dailyAttendance WHERE date = ?', (date_param,))
    student_ids =  cursor.fetchall()[0][0].split(',') # reduce the nested list to a individual elements
    print(student_ids)
    student_phone_dict = {}
    query = "SELECT student_id, phone_numbers FROM studentInfo WHERE student_id = ?"

    # Loop through each student ID and fetch the corresponding phone number
    for student_id in student_ids:
        print(student_id)
        cursor.execute(query, (student_id,))
        result = cursor.fetchone()

        if result:
            student_phone_dict[result[0]] = result[1]

    return student_phone_dict

@app.route('/api/phone-number/<student_id>')
def phone_number_list(student_id):
    db = get_db()
    cursor = db.cursor()
    query = "SELECT phone_numbers FROM studentInfo WHERE student_id = ?"
    cursor.execute(query, (student_id,))
    result = cursor.fetchone()
    phone_numbers_json = json.dumps(result)
    return phone_numbers_json

@app.route('/api/name')
def student_name():
    db = get_db()
    cursor = db.cursor()
    print(request.args.get('id'))
    if request.args.get('id'):
        query = "SELECT student_name FROM studentInfo WHERE student_id = ?"
        cursor.execute(query,(request.args.get('id'),))
        result = cursor.fetchone()
        name = result[0]
        data_dict = {
            "name": name
        }
        return json.dumps(data_dict)
    else:
        return "specifiy a id as the paramter"


extra_dirs = ['./templates/',]
extra_files = extra_dirs[:]
for extra_dir in extra_dirs:
    for dirname, dirs, files in walk(extra_dir):
        for filename in files:
            filename = path.join(dirname, filename)
            if path.isfile(filename):
                extra_files.append(filename)

if __name__ == '__main__':
    app.run(debug=DEBUG, extra_files=extra_files)