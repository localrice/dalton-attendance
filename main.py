from flask import render_template, request, redirect, url_for, Flask
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()
MONGODB_URI = os.environ.get("MONGODB_URI")
client = MongoClient(MONGODB_URI)
db = client.dalton
student_info = db.studentInfo

app = Flask(__name__)

def get_initials(string):
    words = string.split()
    initials = [word[0].upper() for word in words]
    return ''.join(initials)

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
    if request.method == 'GET':
        return f"The URL /data is accessed directly. Try going to '/form' to submit form"

    elif request.method == 'POST':
        form_data = dict(request.form)  # form data from /addStudents
        
        stream_initials = get_initials(form_data.get('stream').title())
        name_initials = get_initials(form_data.get('student name'))
        student_id = stream_initials + name_initials + form_data.get('year1') + form_data.get('year2') + form_data.get('roll number')
        print(student_id)
        form_data['student_id'] = student_id # add student_id in the form
        student_info.insert_one(dict(form_data))

        # check if the data is successfully saved
        result = student_info.find_one({'student_id':student_id})
        if result:
            status = True
        else:
            status = False

        return render_template('data.html', form_data=form_data, status=status)


if __name__ == '__main__':
    app.run(debug=True)