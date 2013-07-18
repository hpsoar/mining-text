from da import db, gen_id, DBObject

class Story(DBObject):
  def __init__(self, url=''):
    self._id = gen_id('stories')
    self.url = url
  
  @property
  def story_id(self):
    return self._id

  def save(self):
    if not self.url:
      print 'invalid story'
    else:
      db.stories.save(self.__dict__)

  @classmethod
  def filter(cls, query):
    return cls.filter_doc(db.stories, query)

  @classmethod
  def get_all(cls):
    return cls.filter({})

  @classmethod
  def get_by_id(cls, story_id):
    stories = cls.filter({'_id': int(story_id) })
    return stories and stories[0]

  @classmethod
  def get_by_url(cls, url):
    stories = cls.filter({'url': url})
    return stories and stories[0]
    


