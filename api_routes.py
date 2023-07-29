from flask import Blueprint, request, g, Flask
import sqlite3
import json
from datetime import datetime

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
            return {'id': student_id, 'name:': result[0]}
        else:
            return {'id': student_id, 'name:': result[0]}
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
                return {'id': student_id, 'error':'No student with the ID could be found'}
            return {'id': result[0], 'name': result[1],'roll_no':result[2],'stream':result[3],'phone_numbers':result[4],'academic_year_from':result[5],'academic_year_to':result[6]}
        else:
            return {'id': result[0], 'name': result[1],'roll_no':result[2],'stream':result[3],'phone_numbers':result[4],'academic_year_from':result[5],'academic_year_to':result[6]}
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
