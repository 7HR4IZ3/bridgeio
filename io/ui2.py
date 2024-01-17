# import threading
import random
# import time
# import json
# from bottle_websocket import WebSocketError
# from bottle import abort

# with open("./jyserver/jyserver.js") as f:
#     JYSERVER = f.read()
from .pybridge import AsyncBridgeProxy

SINGLE_TAGS = [
    'input', 'hr', 'br', 'img', 'area', 'link',
    'col', 'meta', 'base', 'param', 'wbr',
    'keygen', 'source', 'track', 'embed',
]

TAG_NAME_SUBSTITUTES = {
    'del_': 'del',
    'Del': 'del',
}

ATTRIBUTE_NAME_SUBSTITUTES = {
    # html tags colliding with python keywords
    'klass': 'class',
    'Class': 'class',
    'class_': 'class',
    'async_': 'async',
    'Async': 'async',
    'for_': 'for',
    'For': 'for',
    'In': 'in',
    'in_': 'in',

    # from XML
    'xmlns_xlink': 'xmlns:xlink',

    # from SVG ns
    'fill_opacity': 'fill-opacity',
    'stroke_width': 'stroke-width',
    'stroke_dasharray': ' stroke-dasharray',
    'stroke_opacity': 'stroke-opacity',
    'stroke_dashoffset': 'stroke-dashoffset',
    'stroke_linejoin': 'stroke-linejoin',
    'stroke_linecap': 'stroke-linecap',
    'stroke_miterlimit': 'stroke-miterlimit',
}

ATTRIBUTE_VALUE_SUBSTITUTES = {
    'True': 'true',
    'False': 'false',
    'None': 'null',
}

class Ref:
    def __init__(self):
        pass

    def __connect__(self, proxy):
        self.value = proxy

    def __getattr__(self, name):
        if name != "value":
            return getattr(self.value, name)

    def __setattr__(self, name, value):
        if name != "value":
            return setattr(self.value, name, value)
        else:
            setattr(self, name, value)

class Reactive:
    def __init__(self, initial_value=None):
        self.__value = initial_value
        self.__watchers = []

    def __watch__(self, func):
        if func not in self.__watchers and callable(func):
            self.__watchers.append(func)
        return func

    def __unwatch__(self, func):
        if func in self.__watchers:
            self.__watchers.remove(func)
    
    def __trigger_change(self, oldValue):
        for func in self.__watchers:
            func(oldValue, self.__value)

    def set(self, value):
        oldValue = self.__value
        self.__value = value
        self.__trigger_change(oldValue)
        return value

    def get(self):
        return self.__value


class HTML(object):
    """docstring for Form"""

    def __init__(self, response=None, main="html", indentby="\t"):
        self._main = None
        self._mainname = main
        self._indent = 0
        self._indentby = indentby
        self._page = None

        self.response = response

        self.Ref = Ref 
        self.Reactive = Reactive 

    def __getattr__(self, name):
        tag = Tag(name, self, single=name in SINGLE_TAGS)
        if not self._main and name == self._mainname:
            self._main = tag
        return tag
    
    def __getitem__(self, name):
        single = False
        if isinstance(name, tuple):
            name, single = name
        return Tag(name, self, single=single)

    def compile(self):
        return self._main._ret

    def __str__(self):
        return self.compile()


class Tag:
    def __init__(self, name, parent, single=False):
        self._name = name
        self._single = single
        self._parent = parent
        self.attrs = ""
        self.children = []
        self._parent._indent += 1
        self._ret = "<" + self._name

    def __repr__(self):
        return self._ret

    def __str__(self):
        return self._ret

    def __call__(self, *children, **attrs):
        for attr in attrs:
            name = ATTRIBUTE_NAME_SUBSTITUTES.get(attr, attr).replace("_", "-")
            value = ATTRIBUTE_VALUE_SUBSTITUTES.get(attrs[attr], attrs[attr])

            if attr == "ref" and isinstance(value, Ref):
                value.__connect__(AsyncBridgeProxy([], {
                    "location": ""
                }))
            elif attr == "bind":
                pass
            else:
                if isinstance(value, str):
                    self.attrs = self.attrs + \
                        ((f'{name}="{value}" ' if value !=
                        True else f"{name} ") if value else "")
                else:
                    res = self._parent.response
                    if callable(value) and res:
                        temp_name = getattr(
                            value, "__name__",
                            f"temp_func_{random.randint(0, 100000000)}"
                        )
                        res.__register__(temp_name, value)
                        value = temp_name

                        self.attrs = (
                            self.attrs + f'{name}="client.exec(\'{value}_{res.id}\', event, this)" '
                        )
                    else:
                        self.attrs = self.attrs + (
                            (
                                f'{name}="{value}" '
                                if value != True
                                else f"{name} "
                            ) if value else ""
                        )

        self.attrs = self.attrs.strip()
        self._ret = self._ret + " " + self.attrs

        if self._single:
            self._ret = self._ret.strip() + "/>"
        else:
            self._ret = self._ret.strip() + ">"

            for child in children:
                self._ret = self._ret + \
                    f"\n{self._parent._indentby * self._parent._indent}" + \
                    str(child)

            self._ret = self._ret + \
                f"\n{self._parent._indentby * (self._parent._indent - 1) }" + \
                "</" + self._name + ">"

        self._parent._indent -= 1
        return self._ret

# html = HTML()

# html.html(
#     html.head(
#         html.meta(rel="stylesheet")
#     ),
#     html.body(
#         html.header(
#             html.nav(
#                 html.ul(
#                     html.li(html.a("Nav item 1", href="/1")),
#                     html.li(html.a("Nav item 2", href="/2")),
#                     html.li(html.a("Nav item 3", href="/3")),
#                     html.li(html.a("Nav item 4", href="/4")),
#                 )
#             )
#         ),
#         html.main(
#             html.div(
#                 html.h2("Hello World"),
#                 html.p("This is a paragraphed text")
#             )
#         ),
#         html.footer(
#             html.script(
#                 "var i = 0;"
#             )
#         ),
#         html.script(src="./jquery.js")
#     )
# )

# print(html)
