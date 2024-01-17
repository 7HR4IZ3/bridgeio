from .core import MutationObserver, Document
from .tags import create_element

class Ref:
    pass

class Reactive:
    pass

class HTML:
  def __init__(self, response=None):
    self.response = response
    self.__document__ = Document(response=self.response)

  # def Element(self, name):
  #     def wrapper(self):
  #         return type("custom_tag", (dom.Element,), {"name": name})

  def __getattr__(self, name):
      return self[name]

  def __getitem__(self, name):
    def wrapper(*args, **kwargs):
      tag = create_element(name, *args, **kwargs)
      return tag
