from inspect import iscoroutinefunction

class Hooks:

  def __init__(self):
    self.__events = {}

  @property
  def events(self):
    return self.__events

  def on(self, event, callback=None):

    def wrapper(callback):
      self.__events.setdefault(event, []).append(callback)
      return callback

    return wrapper(callback) if callback else wrapper

  def once(self, event, callback):

    async def _(*args, **kwargs):
      if iscoroutinefunction(callback):
        await callback(*args, **kwargs)
      else:
        callback(*args, **kwargs)
      self.__events.get(event).remove(_)

    return self.on(event, _)
  
  def off(self, event, callback):
    if event in self.__events:
      events = self.__events.get(event, [])
      try:
        events.remove(callback)
      except ValueError:
        pass
    return callback

  async def dispatch(self, event, *args, **kwargs):
    for callback in self.__events.get(event, []):
      if iscoroutinefunction(callback):
        await callback(*args, **kwargs)
      else:
        callback(*args, **kwargs)
