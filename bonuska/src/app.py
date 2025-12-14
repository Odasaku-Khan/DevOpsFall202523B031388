from flask import Flask
app = Flask(__name__)
@app.route('/health')
def health():
    return "OK"
@app.route('/hello-world')
def hello_world():
    return "hello, devops 2025"
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
