from flask import Flask, render_template

app = Flask(__name__)

@app.route('/add/<num1>/<num2>')
def add(num1, num2):
    result = float(num1) + float(num2)
    return render_template('index.html', result=result)

@app.route('/subtract/<num1>/<num2>')
def subtract(num1, num2):
    result = float(num1) - float(num2)
    return render_template('index.html', result=result)

@app.route('/multiply/<num1>/<num2>')
def multiply(num1, num2):
    result = float(num1) * float(num2)
    return render_template('index.html', result=result)

@app.route('/divide/<num1>/<num2>')
def divide(num1, num2):
    if float(num2) != 0:
        result = float(num1) / float(num2)
        return render_template('index.html', result=result)
    else:
        return 'Error: Division by zero'

if __name__ == '__main__':
    app.run()
