import feedparser
import os
import datetime
from BeautifulSoup import BeautifulSoup as Soup
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from lxml import etree
from StringIO import StringIO
import HTMLParser
import re
from story import Story
from optparse import OptionParser

def strip_tags(html):
  try:
    if html:
      html2 = HTMLParser.HTMLParser().unescape(html)
      return re.sub('<[^<]+?>', '', html2)
    else:
      return ''
  except Exception, e:
    print '-' * 80
    print 'exception'
    print e
    print html
    print '-' * 80

class NSTree(object):
  @classmethod
  def load(cls, path):
    content = open(path).read()
    parser = etree.XMLParser(recover=True)
    tree = etree.parse(StringIO(content), parser)

    return NSTree(tree.getroot(), { 'n': tree.getroot().nsmap[None] })

  def __init__(self, node, ns):
    self.node = node
    self.ns = ns

  def __getattr__(self, name):
    attr = self.node.__getattribute__(name)
    return attr
    #if name == 'xpath' and hasattr(attr, '__call__'):
    #  def newfunc(*args, **kwargs):
    #    print('before calling %s' %attr.__name__)
    #    result = attr(*args, **kwargs)
    #    print('done calling %s' %attr.__name__)
    #    return result
    #  return newfunc
    #else:
    #  return attr
  
  # TODO: is there a better way?
  def xpath(self, path):
    path = './/n:%s' % path
    result = self.node.xpath(path, namespaces=self.ns) 
    if (isinstance(result, list)):
      return [NSTree(item, self.ns) for item in result]
    else: 
      return NSTree(result, self.ns)

class GRXMLFeed:
  def __init__(self, path):
    print path
    starttime = datetime.datetime.now()
    self.root = NSTree.load(path)
    endtime = datetime.datetime.now() 
    print '-' * 80
    print('(%s-%s) : %s' % (starttime, endtime, endtime-starttime))

  def make_tag(self, tag):
    return '{%s}%s' % (ns, tag)

  def extract_story(self, e):
    link = e.xpath('link')
    #if link: print link[0].attrib['href'] #get node attrib
    url = link and link[0].get('href', '')
    if not url: return None
    story = Story(url)

    title = e.xpath('title')
    story.title = title and title[0].text

    summary = e.xpath('summary') or e.xpath('content')
    story.summary = strip_tags(summary and summary[0].text)

    categories = e.xpath('category')
    published = e.xpath('published')
    updated = e.xpath('updated')
    author = e.xpath('author') # compound data: name, etc.
    #if author: 
    #  name = author[0].xpath('name')
    #  if name: print name[0].text
    source = e.xpath('source') # compound data

    return story

  def extract_stories(self):
    print 'extract_stories'
    return [self.extract_story(e) for e in self.root.xpath('entry')]

def process_file(filename):
  stories = GRXMLFeed(filename).extract_stories()
  for story in stories:
    story.save()


def process(path):
  if not os.path.exists(path):
    print '%s not exists' % path
    return
  
  if os.path.isfile(path):
    return process_file(path)

  for dir_path, subpaths, filenames in os.walk(path):
    for filename in filenames:
      process_file(os.path.join(dir_path, filename))

if __name__ == '__main__':
  parser = OptionParser()
  parser.add_option('-i', "--input", dest="path", help="input file, or path")
  parser.add_option("-l", "--list", action="store_true", dest="list_stories", default=False, help="list stories")
  parser.add_option("-p", "--parse", action="store_true", dest="parse_stories", default=False, help="parse stories from input")

  (options, args) = parser.parse_args()

  if options.parse_stories:
    process(options.path)
  elif options.list_stories:
    stories = Story.get_all()
    for story in stories:
      if not story.url:
        print '-' * 80
        print 'no link'


