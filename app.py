#!venv/bin/python
import csv
from flask import Flask, jsonify, request, redirect, url_for
import json
import requests
from werkzeug.utils import secure_filename


records = []


app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


def allowed_filetype(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() == 'csv'


def correct_filetype_and_fieldnames(filename):
    if not allowed_filetype(filename):
        return False

    with open(filename) as csvfile:
        file_object = csv.DictReader(csvfile, delimiter=',')

        expected_fieldnames = ['firstname', 'lastname', 'birthdate']
        if not file_object.fieldnames == expected_fieldnames:
            return False

    return True


def read_csv(filename):
    line = 1
    new_records = []

    with open(filename) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV:
            if line == 1:
                headers = row
            else:
                new_records.append(
                    dict(zip(headers, row))
                )
            line += 1
    csvfile.close()

    json_records = {'records': new_records}

    requests.post(
        'http://127.0.0.1:5000/post-csv/',
        data=json.dumps(json_records),
        headers={'Content-Type': 'application/json'}
    )


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            return redirect(request.url)

        if not correct_filetype_and_fieldnames(file.filename):
            return redirect(request.url)

        if file:
            filename = secure_filename(file.filename)
            read_csv(filename)
            return redirect(url_for('successfull_upload')), 201
    return '''
    <!doctype html>
    <title>Upload new csv file</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''


@app.route('/post-csv/', methods=['POST'])
def add_records():
    if not request.json or 'records' not in request.json:
        return 'Some error message', 400

    new_records = request.json['records']

    for new_record in new_records:
        records.append(new_record)

    return 'Some good news', 201


@app.route('/success/', methods=['GET'])
def successfull_upload():
    return jsonify(records), 201


if __name__ == '__main__':
    app.run(debug=True)
