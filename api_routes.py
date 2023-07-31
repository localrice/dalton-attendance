from flask import Blueprint, request, g, Flask
import sqlite3
import json
from datetime import datetime
import ast

# some configs
DATABASE = 'dalton.db'

api_bp = Blueprint('api', __name__)
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


@api_bp.route('/api/attendance/<input_string>')
def attendance_list(input_string):
    if request.args.get('date') == 'today':
        date_param = datetime.now().strftime("%d-%m-%Y")
    else:
        date_param = request.args.get('date')
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        f'SELECT {input_string} FROM dailyAttendance WHERE date = ?', (date_param,))
    result = cursor.fetchall()

    # might contain blank values
    student_ids = [
        id for sublist in result for ids in sublist for id in ids.split(',')]
    # removes blank values
    filtered_student_ids = [item for item in student_ids if item.strip()]
    return filtered_student_ids


@api_bp.route('/api/phone-number')
def phone_number_list():
    db = get_db()
    cursor = db.cursor()
    student_id = request.args.get('id')
    if student_id:
        query = 'SELECT phone_numbers FROM studentInfo11 WHERE student_id = ?'
        cursor.execute(query, (student_id,))
        result = cursor.fetchone()
        phone_numbers_json = json.dumps(result)
        if phone_numbers_json == 'null':
            query = 'SELECT phone_numbers FROM studentInfo12 WHERE student_id = ?'
            cursor.execute(query, (student_id,))
            result = cursor.fetchone()
            phone_numbers_json = json.dumps(result)
            

            def process_input(input_str):
                 try:
                     parsed_data = ast.literal_eval(input_str)
                     if isinstance(parsed_data, list):
                         numbers_list = []
                         for item in parsed_data:
                             if isinstance(item, str) and ',' in item:
                                 numbers_list.extend([int(num) for num in item.split(',')])
                             else:
                                 numbers_list.append(int(item))
                         return numbers_list
                     else:
                         print("Input does not represent a list.")
                         return None
                 except (SyntaxError, ValueError):
                     print("Invalid input format.")
                     return None

            return {'id': student_id, 'phone-numbers': process_input(f'{phone_numbers_json}')}
        else:
            return {'id': student_id, 'phone-numbers': phone_numbers_json}
    else:
        return {'error': 'id as an argument should be provided'}


@api_bp.route('/api/name')
def student_name():
    db = get_db()
    cursor = db.cursor()
    student_id = request.args.get('id')
    if student_id:
        query = 'SELECT student_name FROM studentInfo11 WHERE student_id = ?'
        cursor.execute(query, (student_id,))
        result = cursor.fetchone()
        if json.dumps(result) == 'null':
            query = 'SELECT student_name FROM studentInfo12 WHERE student_id = ?'
            cursor.execute(query, (student_id,))
            result = cursor.fetchone()
            if json.dumps(result) == 'null':
                return {'id': student_id, 'name:': 'null'}
            return {'id': student_id, 'name': result[0]}
        else:
            return {'id': student_id, 'name': result[0]}
    else:
        return {'error': 'id as an argument should be provided'}


@api_bp.route('/api/all-info')
def student_info():
    db = get_db()
    cursor = db.cursor()
    student_id = request.args.get('id')
    if student_id:
        query = 'SELECT * FROM studentInfo11 WHERE student_id = ?'
        cursor.execute(query, (student_id,))
        result = cursor.fetchone()
        if json.dumps(result) == 'null':
            query = 'SELECT * FROM studentInfo12 WHERE student_id = ?'
            cursor.execute(query, (student_id,))
            result = cursor.fetchone()
            if json.dumps(result) == 'null':
                return {'id': student_id, 'error': 'No student with the ID could be found'}
            return {'id': result[0], 'name': result[1], 'roll_no': result[2], 'stream': result[3], 'phone_numbers': result[4], 'academic_year_from': result[5], 'academic_year_to': result[6],'class':12}
        else:
            return {'id': result[0], 'name': result[1], 'roll_no': result[2], 'stream': result[3], 'phone_numbers': result[4], 'academic_year_from': result[5], 'academic_year_to': result[6],'class':11}
    else:
        return {'error': 'id as an argument should be provided'}


@api_bp.route('/api/total-students')
def total_students():
    db = get_db()
    cursor = db.cursor()
    requested_stream = request.args.get('stream')
    requested_class = request.args.get('class')
    requested_total = request.args.get('total')
    available_streams = ['arts', 'commerce', 'science']
    available_classes = ['11', '12']
    if requested_stream:
        requested_stream = requested_stream.lower()
    if requested_total:
        requested_total = requested_total.lower()
    if requested_class:
        requested_class = requested_class.lower()
    # when stream is provided (and class too)
    if requested_stream in available_streams:
        if requested_class in available_classes:  # when both stream and class are provided as args
            query = f'SELECT COUNT(*) FROM  StudentInfo{requested_class}  WHERE stream = ?'
            cursor.execute(query, (requested_stream,))
            total_rows = cursor.fetchone()[0]
            return {'stream': requested_stream, 'class': requested_class, 'number_of_students': total_rows}
        else:  # when only stream is provided
            total_students = 0
            for stream_class in available_classes:
                query = f'SELECT COUNT(*) FROM  StudentInfo{stream_class}  WHERE stream = ?'
                cursor.execute(query, (requested_stream,))
                total_rows = cursor.fetchone()[0]
                total_students = total_students+total_rows
                print(total_students)
            return {'stream': requested_stream, 'classes': '11 & 12', 'number_of_students': total_students}
    elif requested_class in available_classes:  # when only class is provided
        total_students = 0
        for stream in available_streams:
            query = f'SELECT COUNT(*) FROm StudentInfo{requested_class} WHERE stream = ?'
            cursor.execute(query, (stream,))
            total_rows = cursor.fetchone()[0]
            total_students = total_students + total_rows
        return {'streams': available_streams, 'class': requested_class, 'number_of_students': total_students}
    elif requested_total == 'true':  # when total=true is requested total number of students is returned back
        total_students = 0
        for stream in available_streams:
            for stream_class in available_classes:
                query = f'SELECT COUNT(*) FROm StudentInfo{stream_class} WHERE stream = ?'
                cursor.execute(query, (stream,))
                total_rows = cursor.fetchone()[0]
                total_students = total_students + total_rows
        return {'streams': available_streams, 'classes': available_classes, 'number_of_students': total_students}
    else:  # read the api docs, if doc ain't available make one yourself
        return 'quack quack, this api is wack'


@api_bp.route('/api/attendance-count')
def count_id_in_present_and_absent():
    db = get_db()
    cursor = db.cursor()
    id = request.args.get('id')
    if id:
        query_present = "SELECT present FROM dailyAttendance;"
        cursor.execute(query_present)
        result = cursor.fetchall()
        count_present = 0
        for item in result:
            string_value = item[0]
            ids = string_value.split(',')
            count_present += ids.count(id)
        query_present = "SELECT absent FROM dailyAttendance;"
        cursor.execute(query_present)
        result = cursor.fetchall()
        count_absent = 0
        for item in result:
            string_value = item[0]
            ids = string_value.split(',')
            count_absent += ids.count(id)
        return {'present': count_present, 'absent': count_absent}
    else:
        return {'error': 'must provide an id'}

@api_bp.route('/api/attendance-taken-or-not')
def attemdance_taken_or_not():
    db = get_db()
    cursor = db.cursor()
    requested_class = request.args.get('class')
    requested_stream = request.args.get('stream')
    requested_date = request.args.get('date')
    if requested_date:
        pass
    else:
        requested_date = datetime.now().strftime("%d-%m-%Y")
    cursor.execute("SELECT COUNT(*) FROM dailyAttendance WHERE stream=? AND date=? AND class=?", (requested_stream, requested_date, requested_class,))
    row_count = cursor.fetchone()[0]
    return {'attendance_taken':row_count>0}