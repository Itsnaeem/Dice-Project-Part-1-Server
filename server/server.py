import os
import random
import hashlib
from flask import Flask, send_file

app = Flask(__name__)

@app.route('/')
def index():
    return 'This is the server. To get a file, go to /get_file.'

@app.route('/get_file')
def get_file():
    file_path = '/app/serverfile.txt'  # Adjusted file path
    file_size = 1024  # 1KB
    random_data = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', k=file_size))
    with open(file_path, 'w') as file:
        file.write(random_data)
    checksum = hashlib.sha256(random_data.encode()).hexdigest()
    return send_file(file_path), 200, {'Checksum': checksum}

if __name__ == '__main__':
    if not os.path.exists('/app'):
        os.makedirs('/app')
    app.run(host='0.0.0.0', port=5000)
