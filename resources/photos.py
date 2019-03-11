from flask import request, current_app, Blueprint, send_file, jsonify
import os

_path = os.path.abspath(os.path.dirname(__file__))
photo_dir = os.path.join(_path, "photos")
try:
  os.mkdir(photo_dir)
except Exception as e:
  print(e)

photos = Blueprint('photos', __name__)

@photos.route('/<photo>', methods=['GET'])
def getPhoto(photo):
  try:
    return send_file(os.path.join(photo_dir, photo))
  except Exception as e:
    res = jsonify({'status': 'failure', 'message': 'photo does not exit'})
    res.status_code = 404
    return res