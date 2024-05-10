from flask import Flask, render_template, request
from libs.mails import make_mail_list

app = Flask(__name__)


@app.route('/')
def hello_pybo():
    return render_template('home.html')

@app.route('/button_click', methods = ['POST'])
def button_click():
    if request.method == 'POST':
        button_action = request.form['button_action']
    return render_template('show_data.html')

if __name__ == '__main__':
    app.run(debug=True)