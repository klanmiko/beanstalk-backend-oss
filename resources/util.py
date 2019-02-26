from models.post import PostSchema
import base64

post_schema = PostSchema()

def mapBinaryImage(image):
   encoded = base64.b64encode(image)
   return 'data:image/jpg;base64,{}'.format(encoded.decode())

def mapPost(post):
   p = post_schema.dump(post).data
   p['photo'] = mapBinaryImage(p['photo'])
   return p