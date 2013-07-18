from pymongo import Connection

_host = '127.0.0.1'
_connection = Connection(_host, 27017)
db = _connection['mining-db']

def gen_id(key_str):
  result = db.ids.find_and_modify(query={'key':key_str}, update={'$inc':{'id':1}}, upsert=True)
  if not result:
    result = db.ids.find_and_modify(query={'key':key_str}, update={'$inc':{'id':10000000}}, upsert=True)
  return result['id']

class DBObject(object):
  def __str__(self):
    return self.__dict__.__str__()

  def __repr__(self):
    return self.__str__()

  @classmethod
  def dict2obj(cls, d):
    o = cls()
    o.__dict__.update(d)
    return o

  @classmethod
  def filter_doc(cls, doc, query):
    return [cls.dict2obj(cur) for cur in doc.find(query)]

