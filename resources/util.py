from models.post import PostSchema
import base64
from uuid import UUID

post_schema = PostSchema()

def mapBinaryImage(image):
   encoded = base64.b64encode(image)
   return 'data:image/jpg;base64,{}'.format(encoded.decode())

def mapPost(post):
   p = post_schema.dump(post).data
   try:
      p['photo'] = str(UUID(bytes=p['photo']))
   except Exception as e:
      print(e)
      p['photo'] = mapBinaryImage(p['photo'])
   return p