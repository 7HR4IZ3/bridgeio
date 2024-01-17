import inspect
import random
import typing as t
from functools import wraps

from .utils import Hooks
from .pybridge import force_sync, async_daemon_task as _

SINGLE_TAGS = [
  "input",
  "hr",
  "br",
  "img",
  "area",
  "link",
  "col",
  "meta",
  "base",
  "param",
  "wbr",
  "keygen",
  "source",
  "track",
  "embed",
]

TAG_NAME_SUBSTITUTES = {
  "del_": "del",
  "Del": "del",
}

ATTRIBUTE_NAME_SUBSTITUTES = {
  # html tags colliding with python keywords
  "klass": "class",
  "Class": "class",
  "class_": "class",
  "async_": "async",
  "Async": "async",
  "for_": "for",
  "For": "for",
  "In": "in",
  "in_": "in",
  # from XML
  "xmlns_xlink": "xmlns:xlink",
  # from SVG ns
  "fill_opacity": "fill-opacity",
  "stroke_width": "stroke-width",
  "stroke_dasharray": " stroke-dasharray",
  "stroke_opacity": "stroke-opacity",
  "stroke_dashoffset": "stroke-dashoffset",
  "stroke_linejoin": "stroke-linejoin",
  "stroke_linecap": "stroke-linecap",
  "stroke_miterlimit": "stroke-miterlimit",
}

ATTRIBUTE_VALUE_SUBSTITUTES = {
  "True": "true",
  "False": "false",
  "None": "null",
}


def configure(
  args=None, as_callback=False,
  response=None, name=None
):
  def wrapper(func):
    func.__pass_args__ = args
    func.__as_callback__ = as_callback

    class wrapped:
      def __init__(self):
        self.response = response

      def __call__(self, *args, **kwargs):
        return func(*args, **kwargs)

      def __str__(self):
        return build_client_callback(func, self.response, name)

      def __getattr__(self, name):
        return getattr(func, name)

    result = wraps(
      func,
      updated=[],
      assigned=["__name__", "__qualname__", "__doc__", "__module__"],
    )(wrapped())
    result.__configured__ = True
    return result

  return wrapper


async def getnodeType(node):
  if isinstance(node, Reactive):
    node = node.get()

  if isinstance(node, (str, int, bool)):
    return 3
  if isinstance(node, Element):
    return node.name.lower()

  ntype = await node.nodeType
  if ntype == 1:
    return (await node.tagName).lower()
  else:
    return ntype


# async def clean(node):
#    for child in await node.childNodes:
#      ntype = await child.nodeType

#      if (
#       child.nodeType === 8 ||
#       (child.nodeType === 3 &&
#          !/\S/.test(child.nodeValue) &&
#          child.nodeValue.includes("\n"))
#      ) {
#         node.removeChild(child)
#         n--
#      } else if (child.nodeType === 1) {
#         clean(child)
#      }
#    }
# }


async def create_element(browser, html, vnode):
  if isinstance(vnode, Reactive):
    vnode = vnode.get()

  if isinstance(vnode, (str, int, bool)):
    return await browser.document.createTextNode(str(vnode))

  tag = await browser.document.createElement(vnode.name)

  for attr in vnode.attributes:
    value = vnode.attributes[attr]

    if callable(value):
      value = build_client_callback(value, html.response)

    await tag.setAttribute(attr, value)

  for child in vnode.children:
    await tag.append(await create_element(browser, html, child))

  return tag


async def attrbutesIndex(el, browser):
  attributes = {}
  attrs = await browser.Array["from"](await el.attributes)

  if not attrs:
    return attributes

  for attr in attrs:
    attributes[await attr.name] = await attr.value

  return attributes


async def patchAttributes(vdom, dom, browser, html):
  vdomAttributes = vdom.attributes
  domAttributes = await attrbutesIndex(dom, browser)

  if vdomAttributes == domAttributes:
    return

  for key in vdomAttributes:
    value = vdomAttributes[key]

    if callable(value):
      value = build_client_callback(value, html.response)

    # if the attribute is not present in dom then add it
    if not domAttributes.get(key):
      await dom.setAttribute(key, value)
    # if the atrtribute is present than compare it
    else:
      if value != domAttributes[key]:
        await dom.setAttribute(key, value)

  for key in domAttributes:
    # if the attribute is not present in vdom than remove it
    if not vdomAttributes.get(key):
      await dom.removeAttribute(key)


async def diff(browser, html, vdom, dom):
  if not dom or not vdom:
    return

  if vdom.attributes.get("data-html-ignore-update"):
    return

  # if dom has no childs then append the childs from vdom
  if not await dom.hasChildNodes() and len(vdom.children) > 0:
    for child in vdom.children:
      # appending
      await dom.append(await create_element(browser, html, child))

  else:
    # if both nodes are equal then no need to compare farther
    if vdom.__compile__(True) == await dom.innerHTML:
      return

    # if dom has extra child
    c_length = await dom.childNodes.length

    if c_length > len(vdom.children):
      count = c_length - len(vdom.children)
      if count > 0:
        # for ( count > 0 count--) {
        while count > 0:
          await dom.childNodes[await dom.childNodes.length - count].remove()
          count -= 1

    # now comparing all childs
    for i, child in enumerate(vdom.children):
      # if the node is not present in dom append it
      dchild = await dom.childNodes[i]

      if isinstance(child, Reactive):
        child = child.get()

      if not dchild:
        await dom.append(await create_element(browser, html, child))
        # console.log("appenidng",vdom.childNodes[i])
      elif await getnodeType(child) == await getnodeType(dchild):
        # if same node type
        # if the nodeType is text

        if isinstance(child, (str, int, bool)):
          # we check if the text content is not same
          if child != await dchild.textContent:
            # replace the text content
            await dchild.__set__("textContent", child)
        elif isinstance(child, Element):
          await patchAttributes(child, dchild, browser, html)

      else:
        # replace
        await dchild.replaceWith(await create_element(browser, html, child))

      if isinstance(child, Element):
        await diff(browser, html, child, dchild)


def build_client_callback(callback, name_or_response=None, func_name=None):
  name = response = None
  if func_name:
    name = func_name

  configured = getattr(callback, "__configured__", False)
  if configured:
    if name_or_response:
      callback.response = name_or_response
    return str(callback)

  if name_or_response:
    if isinstance(name_or_response, str):
      name = name_or_response
    else:
      response = name_or_response

  if response:
    if not name:
      possibleName = response.get_key(callback)
      if possibleName:
        name = possibleName

      name = getattr(callback, "__name__", None)

      if not name or name == "<lambda>":
        name = f"func_{random.randint(0, 9999999)}"

      name = f"{name}_{response.id}"
    else:
      value = response.get_value(name)
      if value and value != callback:
        name = f"{random.randint(0, 999)}{name}"

    response.register(name, callback)

  script = f"client.exec('{name}'"
  arguments = getattr(callback, "__pass_args__", None) or ["event"]

  if arguments:
    arguments = ", ".join(arguments)
    script = script + ", " + arguments
  else:
    arguments = ""

  if getattr(callback, "__as_callback__", False):
    script = f"(...$$$) => " + script + ", ...$$$"

  return script + ")"


class Ref:
  def __init__(self):
    self.__proxy = None

  @property
  def value(self):
    return self.__proxy

  def __connect__(self, proxy):
    self.__proxy = proxy

  def __getattr__(self, name):
    return getattr(self.__proxy, name)

  def __setattr__(self, name, value):
    if name == "_Ref__proxy":
      return super().__setattr__(name, value)
    return setattr(self.__proxy, name, value)


class Reactive(Hooks):
  def __init__(self, initial_value=None):
    self.__value = initial_value
    super().__init__()

  async def set(self, value):
    oldValue = self.__value
    self.__value = value
    await self.dispatch("change", oldValue)
    return value

  def get(self):
    return self.__value


class HTML(Hooks):
  """docstring for Form"""

  Ref = Ref
  Reactive = Reactive

  def __init__(self, response=None, indentby="  "):
    super().__init__()

    self.__indent = 0
    self.__indentby = indentby

    self.__main = None

    self.response = response

  @property
  def __main__(self):
    return self.__main

  def __indent__(self, value=None):
    if value:
      self.__indent = value
    return self.__indent

  @property
  def __indentby__(self):
    return self.__indentby

  def __getattr__(self, name):
    tag = Element(name, self, single=name in SINGLE_TAGS)
    if not self.__main:
      self.__main = tag
    return tag

  def __getitem__(self, name):
    single = name in SINGLE_TAGS
    if isinstance(name, (tuple, list)):
      name, single = name
    return Element(name, self, single=single)

  def __compile__(self, rerender=False):
    return self.__main.__compile__(rerender)

  def __ensure_body__(self):
    if self.__main.name != "html":
      if self.__main.name not in ("head", "body"):
        self.__main = self.body(self.__main)
      self.__main = self.html(self.__main)

  def __str__(self):
    return self.__compile__()


class Element:
  def __init__(self, name, html, single=False):
    self.__single = single or (name in SINGLE_TAGS)

    self.name = name
    self.html = html

    self.parent = None

    self.children = []
    self.attributes = {}

  def __repr__(self):
    return f"Element(name={self.name}, attrs={self.attributes})"

  def __str__(self):
    return self.__compile__()

  def __call__(self, *children, **attrs):
    self.attributes.update(attrs)
    for child in children:
      self.append(child)
    return self

  @property
  def siblings(self):
    if not self.parent:
      return []
    return self.parent.children

  @property
  def isConnected(self):
    return self.parent is not None

  def remove(self, child=None):
    if child:
      child.remove()
    else:
      self.parent = None
      self.parent.children.remove(self)

  def append(self, *children):
    for child in children:
      if isinstance(child, Element):
        if child.isConnected:
          child.remove()

        child.parent = self
      self.children.append(child)

  def __compile__(self, rerender=False):
    end = ""
    body = " "
    attrs = " "
    start_close = ""
    start = "<" + self.name

    refs = {}

    for attr in self.attributes:
      name = ATTRIBUTE_NAME_SUBSTITUTES.get(attr, attr).replace("_", "-")
      value = ATTRIBUTE_VALUE_SUBSTITUTES.get(
        self.attributes[attr], self.attributes[attr]
      )

      if attr == "ref" and isinstance(value, Ref):
        if "id" in self.attributes:
          refs[f"#{self.attributes.get('id')}"] = value
        else:
          ref_id = random.randint(0, 100000)
          refs[f'[ref="{ref_id}"]'] = value

          value = str(ref_id)
      elif attr == "style" and isinstance(value, dict):
        value = ";".join(f"{ikey}: {ivalue}" for ikey, ivalue in value.items())

      if isinstance(value, (str, int, bool)):
        attrs = attrs + (
          (f'{name}="{value}" ' if value != True else f"{name} ")
          if value
          else ""
        )
      elif callable(value):
        if not self.html.response:
          continue

        value = build_client_callback(value, self.html.response)

        attrs = attrs + f'{name}="{value}" '
      else:
        attrs = attrs + (
          (f'{name}="{value}" ' if value != True else f"{name} ")
          if value
          else ""
        )

    if self.html.response and not rerender:

      async def init():
        browser = await self.html.response.get_browser()

        for query, ref in refs.items():
          element = await browser.document.querySelector(query)
          if element:
            ref.__connect__(element)

      self.html.response.once("send", init)

    attrs = attrs.rstrip()

    self.html.__indent__(self.html.__indent__() + 1)

    if self.__single:
      start_close = "/>"
    else:
      start_close = ">"

      for child in self.children:
        body = body + f"\n{self.html.__indentby__ * self.html.__indent__()}"

        if isinstance(child, Reactive):
          if not rerender:

            @child.on("change")
            async def _(*args):
              await self.html.dispatch("update")

          child = child.get()

        if isinstance(child, Element):
          body = body + child.__compile__(rerender)
        else:
          body = body + str(child)

      body = body + f"\n{self.html.__indentby__ * (self.html.__indent__() - 1) }"

      end = "</" + self.name + ">"

    self.html.__indent__(self.html.__indent__() - 1)
    return start + attrs + start_close + body + end

  def transpile(self, handler):
    children = []
    for child in self.children:
      if isinstance(child, Element):
        children.append(child.transpile(handler))
      else:
        children.append(str(child))

    return handler(
      {"name": self.name, "attrs": self.attributes, "children": children}
    )

  async def atranspile(self, handler):
    children = []
    for child in self.children:
      if isinstance(child, Element):
        children.append(await child.atranspile(handler))
      else:
        children.append(str(child))

    return await handler(
      {"name": self.name, "attrs": self.attributes, "children": children}
    )


# html = HTML()

# header = html.header(
#   html.nav(
#    html.ul(
#      html.li(html.a("Nav item 1", href="/1")),
#      html.li(html.a("Nav item 2", href="/2")),
#      html.li(html.a("Nav item 3", href="/3")),
#      html.li(html.a("Nav item 4", href="/4")),
#    )))

# main = html.main(
#   html.div(html.h2("Hello World"), html.p("This is a paragraphed text")))

# footer = html.footer(html.script("var i = 0;"), html.script(src="./jquery.js"))

# dom = html.html(html.head(html.meta(rel="stylesheet")),
#             html.body(header, main, footer))
