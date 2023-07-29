from os import path, walk
from flask import render_template, request, Flask, g
import sqlite3
from datetime import datetime
from utils.check_student_exists import check_student_exists
from utils.id_generator import id_generator
from utils.extract_info import roll_number_from_id
from utils.sort_dict import sort_dict_by_id
from utils.list_string import list_to_string
from api_routes import api_bp
import requests
from utils.fuzzy_search_db import fuzzy_search_names

# some configs
DEBUG = True
DATABASE = 'dalton.db'

app = Flask(__name__)

app.register_blueprint(api_bp)


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
    url_dict = {
        '11': '/attendance/stream?class=11',
        '12': '/attendance/stream?class=12'
    }
    return render_template('infinite_button_links.html', url_dict=url_dict)


@app.route('/attendance/stream')
def stream():
    stream_class = request.args.get('class')
    url_dict = {
        'science': f'/attendance/stream/science?class={stream_class}',
        'commerce': f'/attendance/stream/commerce?class={stream_class}',
        'arts': f'/attendance/stream/arts?class={stream_class}'
    }
    return render_template('infinite_button_links.html', url_dict=url_dict)


@app.route('/attendance/stream/<stream_name>', methods=['GET', 'POST'])
def stream_attendance(stream_name):
    db = get_db()
    cursor = db.cursor()
    stream_class = request.args.get('class')
    table_name = f'StudentInfo{stream_class}'
    cursor.execute(
        f'SELECT student_id FROM {table_name} WHERE stream = ?', (stream_name,))
    results = cursor.fetchall()
    # stores all the id of the students present in the stream without the academic year at the end
    student_id = [result[0] for result in results]

    cursor.execute(
        f'SELECT student_name FROM {table_name} WHERE stream = ?', (stream_name,))
    results = cursor.fetchall()
    # stores all the names of the students present in the stream
    student_names = [result[0] for result in results]

    # creates a dictionary with the key as student's id and value as student's name arranged in increasing order of the roll number in the student id
    student_info = sort_dict_by_id(dict(zip(student_id, student_names)))

    if request.method == 'POST':
        selected_id = list(request.form.to_dict().keys())
        absent_student_ids = list(set(selected_id) ^ set(student_id))
        date = datetime.now().date().strftime("%d-%m-%Y")
        sql_insert = "INSERT INTO dailyAttendance (date, class, stream, present, absent) VALUES (?, ?, ?, ?, ?)"
        data = (date, stream_class, stream_name, list_to_string(selected_id),
                list_to_string(absent_student_ids))
        cursor.execute(sql_insert, data)
        db.commit()
        return render_template('attendance_taken.html', stream_name=stream_name, student_info=student_info,
                               present_students=selected_id, absent_students=absent_student_ids,
                               len=len, max=max, str=str)

    attendance_taken_or_not = requests.get(
        f'http://localhost:5000/api/attendance-taken-or-not?stream={stream_name}&class={stream_class}').json()['attendance_taken']
    return render_template('stream_attendance.html', student_info=student_info, roll_number_from_id=roll_number_from_id, attendance_taken_or_not=attendance_taken_or_not, stream_class=stream_class, stream_name=stream_name)


@app.route('/add-students')
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
        student_class = form_data.get('class')
        student_name = form_data.get('student name')
        year1 = int(form_data.get('year1'))
        year2 = int(form_data.get('year2'))
        phone_numbers_str = request.form.get('phone_numbers')
        phone_numbers = phone_numbers_str.split(
            ',') if phone_numbers_str else []
        student_id = id_generator(
            stream=stream, roll_number=roll_no, name=student_name, year1=year1, year2=year2)
        # if student_id doesn't exist yet, creates a column with the given data
        if student_class == '11':
            table_name = 'studentInfo11'
        else:
            table_name = 'studentInfo12'
        is_student_found = check_student_exists(
            db=db, table_name=table_name, student_id=student_id)
        if is_student_found == False:
            sql_insert = f'INSERT INTO {table_name} (student_id, student_name, roll_no, stream, phone_numbers, academic_year_from, academic_year_to) VALUES (?, ?, ?, ?, ?, ?, ?)'
            data = (student_id, form_data.get('student name'), int(
                roll_no), stream, list_to_string(phone_numbers), year1, year2)
            cursor.execute(sql_insert, data)
            db.commit()
        elif is_student_found == 1:
            return "Roll no., stream, and academic year matches with another student."
        else:
            return render_template('student_already_exists.html')
        # check if the data is successfully saved
        status = check_student_exists(
            db=db, table_name=table_name, student_id=student_id)
        return render_template('data.html', form_data=form_data, status=status)


@app.route('/students/', methods=['POST', 'GET'])
def students():
    total_students = requests.get(
        'http://localhost:5000/api/total-students?total=true').json()['number_of_students']
    present_students = len(requests.get(
        'http://localhost:5000/api/attendance/present?date=today').json())
    percentage = round((present_students / total_students) * 100)
    return render_template('students.html', percentage=percentage)


@app.route('/students/search', methods=['POST', 'GET'])
def search():
    db = get_db()
    cursor = db.cursor()
    if request.method == "POST":
        search_value = request.form.get('search_query')
        similar_names = fuzzy_search_names(
            search_value, db=db, table_name='StudentInfo12')
        similar_ids = [values for key, values in similar_names.items()]
        list_of_info = []
        for id in similar_ids:
            student_info = requests.get(
                f'http://localhost:5000/api/all-info?id={id}').json()
            list_of_info.append(student_info)
        if 'error' in similar_names:
            if similar_names['error'] == 'unsafe searched_name':
                return
            return render_template('students.html', error=f'no student with the name {search_value}')
        else:
            id_attendance_count_list = []

            for id in similar_ids:
                attendance_count = requests.get(
                    f'http://localhost:5000/api/attendance-count?id={id}').json()
                attendance_count['id'] = id
                id_attendance_count_list.append(attendance_count)
            return render_template('students.html', list_of_info=list_of_info, id_attendance_count_list=id_attendance_count_list, enumerate=enumerate, round=round)


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
