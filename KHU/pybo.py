from flask import Flask, render_template, request, jsonify
from libs.mails import make_mail_list
#import database

app = Flask(__name__)


@app.route('/')
def hello_pybo():
    # a = make_mail_list()
    # a = a.iloc[0:5]
    # return render_template('home.html', df = a)

@app.route('/button_click', methods = ['POST'])
def button_click():
    if request.method == 'POST':
        button_action = request.form['button_action']
    return render_template('result.html', df = a)

@app.route('/get-email', methods=['GET'])
def get_email():
    a = make_mail_list()
    return a


if __name__ == '__main__':
    app.run(debug=True)