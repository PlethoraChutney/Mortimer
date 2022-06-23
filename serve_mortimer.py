import os
import couchdb
import glob
from flask import Flask, render_template, request, send_from_directory
import json

class Database(object):
    def __init__(self) -> None:
        host = os.environ['COUCHDB_HOST']
        username = os.environ['COUCHDB_USERNAME']
        password = os.environ['COUCHDB_PASSWORD']
        self.server = couchdb.Server(f'http://{username}:{password}@{host}:5984')

        if 'mortimer_sessions' in self.server:
            self.sessions_db = self.server['mortimer_sessions']
        else:
            self.sessions_db = self.server.create('mortimer_sessions')

    @property
    def sessions(self):
        session_dict = self.sessions_db.get('sessions')
        if session_dict is None:
            return []
        else:
            return list(session_dict.keys())

app = Flask(
    __name__,
    static_folder=os.path.join('dist', 'static'),
    template_folder='dist'
)

db = Database()

@app.route('/', methods = ['GET'])
def index():
    return render_template('index.html')

@app.route('/api', methods = ['POST'])
def api():
    rj = request.get_json()

    if rj['action'] == 'get_sessions':
        sessions = db.sessions_db.get('sessions')
        if sessions is None:
            sessions = {}
        else:
            del sessions['_id']
            del sessions['_rev']
        
        return json.dumps({'sessions': sessions}), 200, {'ContentType': 'application/json'}
    elif rj['action'] == 'check_images':
        path = rj['path'].replace('/image', '')
        if not path or not os.path.exists(path):
            image_paths = []
        else:
            image_paths = glob.glob(f'{path}/grid{rj["grid"]}/aligned_*.png')
            image_paths = ['/image' + x for x in image_paths]

        return json.dumps({'image_paths': image_paths}), 200, {'ContentType': 'application/json'}

@app.route('/image/<path:image_path>', methods = ['GET'])
def image(image_path):
    if image_path[-4:] == '.png':
        image_path = image_path.replace('goliath/rawdata/BaconguisLab/', '')
        app.logger.info(image_path)
        return send_from_directory('/goliath/rawdata/BaconguisLab/', image_path)