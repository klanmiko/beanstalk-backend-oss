from models.post import PostSchema
import base64

post_schema = PostSchema()

def mapPost(post):
  p = post_schema.dump(post).data
  encoded = base64.b64encode(p['photo'])
  p['photo'] = 'data:image/jpg;base64,{}'.format(encoded.decode())
  return p