import inspect
import sys
import asyncio
import typing as t

from functools import wraps
from threading import Event

from starlette.requests import Request
from starlette.applications import Starlette
from starlette.websockets import WebSocket, WebSocketState
from starlette.responses import PlainTextResponse, Response

from .pybridge import (
  AsyncMultiServer, BridgeJS, daemon_task,
  force_sync, async_daemon_task, run_sync,
  generate_random_id, INJECTED_SCRIPT_SRC
)

from .utils import Hooks

from .dom.helpers import generate_xpath
from .dom import HTML as DOMHTML, MutationObserver, core
from .ui import HTML, Element, diff, build_client_callback, configure

if t.TYPE_CHECKING:
  ResponseData = t.TypeVar("ResponseData")


class WebSocketWrapper:

  def __init__(self, socket):
    self.socket = socket

  def __getattr__(self, name):
    return getattr(self.socket, name)

  def receive(self, *args, **kwargs):
    return self.socket.receive_text(*args, **kwargs)

  def send(self, *args, **kwargs):
    return self.socket.send_text(*args, **kwargs)

  @property
  def closed(self):
    return self.socket.client_state == WebSocketState.DISCONNECTED


class BridgeResponse(Response, Hooks):
  RESPONSE_NOT_SENT = 0
  RESPONSE_SENT = 1

  media_type = "text/html"

  def __init__(self, *args, server=None, simple=False, **kwargs):
    self.status = self.RESPONSE_NOT_SENT

    self.__browser = None
    self.__server = server
    self.__simple = simple
    self.__queue = asyncio.Queue()

    if not self.__simple:
      self.__conn_id, self.__script = self.__server.new_connection()

    Hooks.__init__(self)
    super().__init__(*args, **kwargs)

  @property
  def id(self):
    return self.__conn_id
  
  @property
  def __context__(self) -> dict:
    return self.__server.exec_context

  def register(self, name, func):
    self.__context__[name] = func

  def get_key(self, item):
    for key, value in self.__context__.items():
      if value == item:
        return key
    return None
  
  def get_value(self, key):
    return self.__context__.get(key)
  
  def __ensure_body(self, element, html):
    if element.name != "html":
      if element.name not in ("head", "body"):
        element = html.html(
          html.head(), html.body(element)
        )
      else:
        element = html.html(element)
    return element
  
  def __generate_callback(self, event, element, callbacks):
    def wrapper(_event, this):
      for callback in [
        getattr(element, event, None),
        *callbacks
      ]:
        if callable(callback):
          try:
            callback(_event, this=this)
          except:
            pass

    wrapper.__name__ = event
    return configure(
      args=["event", "this"], response=self
    )(wrapper)
  
  def __setup_document(self, document: core.Document):
    for element in core.GLOBAL_LISTENERS:
      listeners= core.GLOBAL_LISTENERS[element]
      for eventType in listeners:
        callbacks = listeners[eventType]
        if len(callbacks) == 0:
          continue

        event = "on" + eventType

        if len(callbacks) == 1:
          element.setAttribute(
            event, build_client_callback(callbacks[0], self)
          )
          continue

        cb = self.__generate_callback(event, element, callbacks)
        element.setAttribute(event, str(cb))

    self.__observer = MutationObserver(self.__make_mutations, 0.1)
    self.__observer.observe(
      document.children[0], childList=True, subtree=True,
      attributes=True, characterData=True
    )
    
    return document

  async def __clone_element(self, node: core.Element, browser):
    tag = await browser.document.createElement(node.tagName)

    for (attr, value) in node.attributes.items():
      if callable(value):
        value = build_client_callback(value, self)
      await tag.setAttribute(attr, value)

    for child in node.childNodes:
      await tag.appendChild(
        await self.__clone_element(child, browser)
      )

  @run_sync
  async def __make_mutations(self, mutations: list[core.MutationRecord]):
    try:
      browser = await self.get_browser()
    except Exception:
      return

    for mutation in mutations:
      vdom_target = mutation.target
      xpath = generate_xpath(vdom_target)
      dom_target = await browser.JSBridge.evalXpath(xpath)

      if await browser.Boolean(dom_target):
        dom_target = await dom_target.singleNodeValue
      else:
        continue

      if mutation.type == "attributes":
        attr = mutation.attributeName
        if attr and attr != "style":
          await dom_target.setAttribute(
            attr, str(vdom_target.getAttribute(attr))
          )
      elif mutation.type == "style":
        name = mutation.attributeName
        await dom_target.style.__set__(
          name, getattr(vdom_target.style, name)
        )
      elif mutation.type == "childList":
        for node in mutation.addedNodes:
          await dom_target.appendChild(
            await self.__clone_element(node, browser)
          )

        for (node, node_xpath) in mutation.removedNodes:
          removed_node = await browser.JSBridge.evalXpath(node_xpath)
          if await browser.Boolean(removed_node):
            removed_node = await removed_node.singleNodeValue
            removed_node.remove()

      elif mutation.type == "characterData":
        if mutation.attributeName in ("innerHTML", "innerText", "textContent"):
          await dom_target.__set__(
            mutation.attributeName, getattr(
              vdom_target, mutation.attributeName
            )
          )

  async def send(self, data: "ResponseData") -> "ResponseData":
    if self.status == self.RESPONSE_NOT_SENT:
      self.status = self.RESPONSE_SENT

      response = data

      if isinstance(response, Response):
        response = response.body.decode()
      elif isinstance(response, (HTML, Element)):
        if isinstance(response, Element):
          html = response.html
        else:
          html = response
          response = html.__main__

        response = self.__ensure_body(response, html)

        @html.on("update")
        async def _():
          browser = await self.get_browser()
          await browser.JSBridge.cleanDom()

          await diff(
            browser, html, response,
            await browser.document.children[0]
          )

        if not self.__simple:
          script1 = html.script(src=INJECTED_SCRIPT_SRC)
          script2 = html.script(self.__script)
  
          response.append(script1, script2)

        return await self.__queue.put(response.__compile__())
      elif isinstance(response, (DOMHTML, core.Document, core.Element)):
        document = response.ownerDocument
        if not document:
          document = core.Document()
          if response.name in ["head", "body"]:
            document.head.remove()
            document.body.remove()

            document.children[0].appendChild(response)
          else:
            document.body.appendChild(response)

        document = self.__setup_document(document)
        response = str(document)

      if self.__simple:
        await self.__queue.put(str(response))
      else:
        await self.__queue.put(
          f'<script src="{INJECTED_SCRIPT_SRC}"></script>' +
          f'<script>{self.__script}</script>' + str(response)
        )
    else:
      browser = await self.get_browser()
      await browser.document.writeLn(str(response))
    return data


  async def get_browser(self):
    if self.__simple:
      raise TypeError("You can't access the browser in a simple response.")

    if not self.__browser:
      self.__browser = await self.__server.get_connection(self.__conn_id)

    return self.__browser

  def get(self):
    return self.__queue.get()


class BridgeIO(Starlette):

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    self.server = AsyncMultiServer()

    super().route(f"{INJECTED_SCRIPT_SRC}")(self.__bridge_js)
    self.websocket_route("/__web_route_ws__/{conn_id:str}")(
      self.__websocket_handler
    )

  async def __websocket_handler(self, websocket: WebSocket):
    conn_id = websocket.path_params['conn_id']

    await websocket.accept()
    try:
      await self.server.handle_connection(WebSocketWrapper(websocket), conn_id)
    finally:
      print(conn_id, self.server.exec_context)
      for key in list(self.server.exec_context.keys()):
        if key.endswith(conn_id):
          self.server.exec_context.pop(key)
      print(conn_id, self.server.exec_context)

  def __bridge_js(self, request):
    return PlainTextResponse(BridgeJS)

  def __route_wrapper(self, func):

    @wraps(func)
    async def wrapper(request):
      response = BridgeResponse(server=self.server)

      @async_daemon_task
      async def background():
        task1 = asyncio.create_task(func(request, response))
        task2 = asyncio.create_task(response.dispatch("send"))
        await asyncio.gather(task1, task2)

      background()

      response.body = response.render(await response.get())
      response.init_headers()

      return response

    return wrapper

  def route(self, *args, **kwargs):
    origRoute = super().route

    def wrapper(func):
      return origRoute(*args, **kwargs)(self.__route_wrapper(func))

    return wrapper

  def run(self):
    from aiohttp import web
    from aiohttp_asgi import ASGIResource

    aiohttp_app = web.Application()
    asgi_resource = ASGIResource(self, root_path="/")
    aiohttp_app.router.register_resource(asgi_resource)
    asgi_resource.lifespan_mount(aiohttp_app)

    try:
      print("* Starting server...")
      web.run_app(aiohttp_app)
    except KeyboardInterrupt as e:
      print("* Stopping server...")

    self.server.stop()
    sys.exit(0)
