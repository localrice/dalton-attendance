from flask import render_template, request, redirect, url_for, Flask


app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('index.html')

@app.route('/attendance', methods=['GET','POST'])
def attendance():
    if request.method == 'POST':
        selected_names = request.form.getlist('name')
        print(selected_names)
    names = ['kevi', 'hated', 'duck', 'neva']

    return render_template('attendance.html', names=names)

if __name__ == '__main__':
    app.run(debug=True)