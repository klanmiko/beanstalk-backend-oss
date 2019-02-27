from flask import request, current_app, Blueprint, send_file
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
  return send_file(os.path.join(photo_dir, photo))