from . import core


def html(*args, document=None, **kwargs) -> "core.HTMLElement":
    document = document or core.Document()
    document.children[0].remove()

    tag = core.HTMLElement(*args, **kwargs)
    return document.appendChild(tag)


# html: type[core.HTMLDocument] = type("html", (core.HTMLDocument,), {"name": "html"})

body: type[core.HTMLBodyElement] = type(
    "body", (core.HTMLBodyElement,), {"name": "body"}
)
head: type[core.HTMLHeadElement] = type(
    "head", (core.HTMLHeadElement,), {"name": "head"}
)
script: type[core.HTMLScriptElement] = type(
    "script", (core.HTMLScriptElement,), {"name": "script"}
)
style: type[core.HTMLStyleElement] = type(
    "style", (core.HTMLStyleElement,), {"name": "style"}
)
h1: type[core.HTMLHeadingElement] = type(
    "h1", (core.HTMLHeadingElement,), {"name": "h1"}
)
h2: type[core.HTMLHeadingElement] = type(
    "h2", (core.HTMLHeadingElement,), {"name": "h2"}
)
h3: type[core.HTMLHeadingElement] = type(
    "h3", (core.HTMLHeadingElement,), {"name": "h3"}
)
h4: type[core.HTMLHeadingElement] = type(
    "h4", (core.HTMLHeadingElement,), {"name": "h4"}
)
h5: type[core.HTMLHeadingElement] = type(
    "h5", (core.HTMLHeadingElement,), {"name": "h5"}
)
h6: type[core.HTMLHeadingElement] = type(
    "h6", (core.HTMLHeadingElement,), {"name": "h6"}
)
p: type[core.HTMLParagraphElement] = type(
    "p", (core.HTMLParagraphElement,), {"name": "p"}
)

i: type[core.Element] = type("i", (core.Element,), {"name": "i"})  # TODO - check which?
b: type[core.Element] = type("b", (core.Element,), {"name": "b"})  # TODO - check which?
portal: type[core.Element] = type(
    "portal", (core.Element,), {"name": "portal"}
)  # TODO - check which?


def Atag(self, *args, **kwargs):
    # print('Atag: ', args, kwargs)
    # Node.__init__(self, *args, **kwargs)
    # core.Element.__init__(self, *args, **kwargs)

    # TODO - fix BUG. this stops having no href on a tags
    if kwargs.get("_href", None) is not None:
        core.URL.__init__(self, url=kwargs["_href"])
    # else:
    # Node.__init__(*args, **kwargs)
    core.Element.__init__(self, *args, **kwargs)
    # Node.__init__(self, *args, **kwargs)
    # URL.__init__(self, *args, **kwargs)


def __update__(
    self, *args, **kwargs
):  # TODO - you removed this but where the unit test that you wrote it for in the first place?
    # print('__update__: ', args, kwargs)
    # URL.__update__(self)
    # TODO - fix BUG. this stops having no href on a tags
    if self.getattr("_href", None) is not None:
        self.kwargs["_href"] = self.href
    # Node.__init__(self, *args, **kwargs)
    # URL.__init__(self, *args, **kwargs)
    # self.__init__(*args, **kwargs)
    core.Element.__init__(self, *args, **kwargs)
    core.URL.__init__(self, *args, **kwargs)


a: type[core.Element] = type(
    "a", (core.Element, core.URL), {"name": "a", "__init__": Atag}
)
# , "__update__": __update__})

ul: type[core.HTMLUListElement] = type("ul", (core.HTMLUListElement,), {"name": "ul"})
ol: type[core.HTMLOListElement] = type("ol", (core.HTMLOListElement,), {"name": "ol"})
li: type[core.HTMLLIElement] = type("li", (core.HTMLLIElement,), {"name": "li"})
div: type[core.HTMLDivElement] = type("div", (core.HTMLDivElement,), {"name": "div"})

strong: type[core.Element] = type(
    "strong", (core.Element,), {"name": "strong"}
)  # TODO - check
blockquote: type[core.Element] = type(
    "blockquote", (core.Element,), {"name": "blockquote"}
)  # TODO - check
table: type[core.HTMLTableElement] = type(
    "table", (core.HTMLTableElement,), {"name": "table"}
)
tr: type[core.Element] = type("tr", (core.Element,), {"name": "tr"})
td: type[core.Element] = type("td", (core.Element,), {"name": "td"})


class form(core.HTMLFormElement):
    def __init__(self, *args, **kwargs):
        new_kwargs = {}
        for k, v in kwargs.items():
            if k[0] != "_":
                # print("WARNING: kwarg '{}' should begin with an underscore".format(k))
                new_kwargs[f"_{k}"] = v
            else:
                new_kwargs[k] = v
        kwargs = new_kwargs

        self.name = "form"
        core.Node.__init__(self, *args, **kwargs)
        core.Element.__init__(self, *args, **kwargs)

    @property
    def elements(self):
        kids = []
        for child in self.children:
            if isinstance(
                child, (button, fieldset, input, object, output, select, textarea)
            ):
                kids.append(child)
        return kids


label: type[core.Element] = type("label", (core.Element,), {"name": "label"})
# label.__doc__ = '''
#         .. highlight:: python
#         .. code-block:: python

#           # used to label form elements. i.e.
#           label(_for=None, _text=None, **kwargs)
#           # <label for=""></label>
#         '''

submit: type[core.Element] = type("submit", (core.Element,), {"name": "submit"})
title: type[core.HTMLTitleElement] = type(
    "title", (core.HTMLTitleElement,), {"name": "title"}
)
noscript: type[core.Element] = type("noscript", (core.Element,), {"name": "noscript"})
section: type[core.Element] = type("section", (core.Element,), {"name": "section"})
nav: type[core.Element] = type("nav", (core.Element,), {"name": "nav"})
article: type[core.Element] = type("article", (core.Element,), {"name": "article"})
aside: type[core.Element] = type("aside", (core.Element,), {"name": "aside"})
hgroup: type[core.Element] = type("hgroup", (core.Element,), {"name": "hgroup"})
address: type[core.Element] = type("address", (core.Element,), {"name": "address"})
pre: type[core.HTMLPreElement] = type("pre", (core.HTMLPreElement,), {"name": "pre"})
dl: type[core.Element] = type("dl", (core.Element,), {"name": "dl"})
dt: type[core.Element] = type("dt", (core.Element,), {"name": "dt"})
dd: type[core.Element] = type("dd", (core.Element,), {"name": "dd"})
figure: type[core.Element] = type("figure", (core.Element,), {"name": "figure"})
figcaption: type[core.Element] = type(
    "figcaption", (core.Element,), {"name": "figcaption"}
)
em: type[core.Element] = type("em", (core.Element,), {"name": "em"})
small: type[core.Element] = type("small", (core.Element,), {"name": "small"})
s: type[core.Element] = type("s", (core.Element,), {"name": "s"})
cite: type[core.Element] = type("cite", (core.Element,), {"name": "cite"})
q: type[core.Element] = type("q", (core.Element,), {"name": "q"})
dfn: type[core.Element] = type("dfn", (core.Element,), {"name": "dfn"})
abbr: type[core.Element] = type("abbr", (core.Element,), {"name": "abbr"})
code: type[core.Element] = type("code", (core.Element,), {"name": "code"})
var: type[core.Element] = type("var", (core.Element,), {"name": "var"})
samp: type[core.Element] = type("samp", (core.Element,), {"name": "samp"})
kbd: type[core.Element] = type("kbd", (core.Element,), {"name": "kbd"})
sub: type[core.Element] = type("sub", (core.Element,), {"name": "sub"})
sup: type[core.Element] = type("sup", (core.Element,), {"name": "sup"})
u: type[core.Element] = type("u", (core.Element,), {"name": "u"})
mark: type[core.Element] = type("mark", (core.Element,), {"name": "mark"})
ruby: type[core.Element] = type("ruby", (core.Element,), {"name": "ruby"})
rt: type[core.Element] = type("rt", (core.Element,), {"name": "rt"})
rp: type[core.Element] = type("rp", (core.Element,), {"name": "rp"})
bdi: type[core.Element] = type("bdi", (core.Element,), {"name": "bdi"})
bdo: type[core.Element] = type("bdo", (core.Element,), {"name": "bdo"})
span: type[core.HTMLSpanElement] = type(
    "span", (core.HTMLSpanElement,), {"name": "span"}
)
ins: type[core.Element] = type("ins", (core.Element,), {"name": "ins"})
iframe: type[core.Element] = type("iframe", (core.Element,), {"name": "iframe"})
video: type[core.HTMLVideoElement] = type(
    "video", (core.HTMLVideoElement,), {"name": "video"}
)
audio: type[core.HTMLAudioElement] = type(
    "audio", (core.HTMLAudioElement,), {"name": "audio"}
)
canvas: type[core.HTMLCanvasElement] = type(
    "canvas", (core.HTMLCanvasElement,), {"name": "canvas"}
)
caption: type[core.Element] = type("caption", (core.Element,), {"name": "caption"})
colgroup: type[core.Element] = type("colgroup", (core.Element,), {"name": "colgroup"})
tbody: type[core.Element] = type("tbody", (core.Element,), {"name": "tbody"})
thead: type[core.Element] = type("thead", (core.Element,), {"name": "thead"})
tfoot: type[core.Element] = type("tfoot", (core.Element,), {"name": "tfoot"})
th: type[core.Element] = type("th", (core.Element,), {"name": "th"})
fieldset: type[core.HTMLFieldSetElement] = type(
    "fieldset", (core.HTMLFieldSetElement,), {"name": "fieldset"}
)
legend: type[core.Element] = type("legend", (core.Element,), {"name": "legend"})
button: type[core.HTMLButtonElement] = type(
    "button", (core.HTMLButtonElement,), {"name": "button"}
)
select: type[core.HTMLSelectElement] = type(
    "select", (core.HTMLSelectElement,), {"name": "select"}
)
datalist: type[core.HTMLDataListElement] = type(
    "datalist", (core.HTMLDataListElement,), {"name": "datalist"}
)
optgroup: type[core.HTMLOptGroupElement] = type(
    "optgroup", (core.HTMLOptGroupElement,), {"name": "optgroup"}
)
option: type[core.HTMLOptionElement] = type(
    "option", (core.HTMLOptionElement,), {"name": "option"}
)
textarea: type[core.HTMLTextAreaElement] = type(
    "textarea", (core.HTMLTextAreaElement,), {"name": "textarea"}
)
output: type[core.HTMLOutputElement] = type(
    "output", (core.HTMLOutputElement,), {"name": "output"}
)
progress: type[core.HTMLProgressElement] = type(
    "progress", (core.HTMLProgressElement,), {"name": "progress"}
)
meter: type[core.HTMLMeterElement] = type(
    "meter", (core.HTMLMeterElement,), {"name": "meter"}
)
details: type[core.Element] = type("details", (core.Element,), {"name": "details"})
summary: type[core.Element] = type("summary", (core.Element,), {"name": "summary"})
menu: type[core.Element] = type("menu", (core.Element,), {"name": "menu"})
# dead but may be used
menuitem: type[core.Element] = type("menuitem", (core.Element,), {"name": "menuitem"})

font: type[core.Element] = type("font", (core.Element,), {"name": "font"})
header: type[core.Element] = type("header", (core.Element,), {"name": "header"})
footer: type[core.Element] = type("footer", (core.Element,), {"name": "footer"})
# map_ = type('map_', (tag,), {'name': 'map_'})
# object_ = type('object_', (tag,), {'name': 'object_'})
# del_ = type('del_', (tag,), {'name': 'del_'})

# time = core.HTMLTimeElement  # type('time', (tag,), {'name': 'time'})
data: type[core.HTMLDataElement] = type(
    "data", (core.HTMLDataElement,), {"name": "data"}
)
samp: type[core.Element] = type("samp", (core.Element,), {"name": "samp"})

base: type[core.HTMLBaseElement] = type(
    "base", (core.HTMLBaseElement,), {"name": "base"}
)
link: type[core.HTMLLinkElement] = type(
    "link", (core.closed_tag, core.HTMLLinkElement), {"name": "link"}
)
# core.HTMLLinkElement TODO - closed tags
meta: type[core.HTMLMetaElement] = type(
    "meta", (core.closed_tag, core.HTMLMetaElement), {"name": "meta"}
)
# core.HTMLMetaElement TODO - closed tags
hr: type[core.HTMLHRElement] = type(
    "hr", (core.closed_tag, core.HTMLHRElement), {"name": "hr"}
)
br = type(
    "br",
    (
        core.closed_tag,
        core.HTMLBRElement,
    ),
    {"name": "br"},
)
wbr: type[core.Element] = type("wbr", (core.closed_tag, core.Element), {"name": "wbr"})
img: type[core.HTMLImageElement] = type(
    "img", (core.closed_tag, core.HTMLImageElement), {"name": "img"}
)
param: type[core.HTMLParamElement] = type(
    "param", (core.closed_tag, core.HTMLParamElement), {"name": "param"}
)
source: type[core.HTMLSourceElement] = type(
    "source", (core.closed_tag, core.HTMLSourceElement), {"name": "source"}
)
track: type[core.HTMLTrackElement] = type(
    "track", (core.closed_tag, core.HTMLTrackElement), {"name": "track"}
)
area: type[core.HTMLAreaElement] = type(
    "area", (core.HTMLAreaElement,), {"name": "area"}
)
col: type[core.HTMLTableColElement] = type(
    "col", (core.closed_tag, core.HTMLTableColElement), {"name": "col"}
)
input: type[core.HTMLInputElement] = type(
    "input", (core.closed_tag, core.HTMLInputElement), {"name": "input"}
)
keygen: type[core.HTMLKeygenElement] = type(
    "keygen", (core.closed_tag, core.HTMLKeygenElement), {"name": "keygen"}
)
command: type[core.Element] = type(
    "command", (core.closed_tag, core.Element), {"name": "command"}
)

main: type[core.Element] = type("main", (core.Element,), {"name": "main"})

# obsolete
applet: type[core.Element] = type("applet", (core.Element,), {"name": "applet"})
# object = type('object', (core.Element,), {'name': 'object'})
basefont: type[core.HTMLBaseFontElement] = type(
    "basefont", (core.HTMLBaseFontElement,), {"name": "basefont"}
)
center: type[core.Element] = type("center", (core.Element,), {"name": "center"})
# dir = type('dir', (core.Element,), {'name': 'dir'})
embed: type[core.HTMLEmbedElement] = type(
    "embed", (core.HTMLEmbedElement,), {"name": "embed"}
)
isindex: type[core.Element] = type("isindex", (core.Element,), {"name": "isindex"})
listing: type[core.Element] = type("listing", (core.Element,), {"name": "listing"})
plaintext: type[core.Element] = type(
    "plaintext", (core.Element,), {"name": "plaintext"}
)
s: type[core.Element] = type("s", (core.Element,), {"name": "s"})
u: type[core.Element] = type("u", (core.Element,), {"name": "u"})
strike: type[core.Element] = type("strike", (core.Element,), {"name": "strike"})
xmp: type[core.Element] = type("xmp", (core.Element,), {"name": "xmp"})

template: type[core.Element] = type("template", (core.Element,), {"name": "template"})

picture: type[core.HTMLPictureElement] = type(
    "picture", (core.HTMLPictureElement,), {"name": "picture"}
)
dialog: type[core.HTMLDialogElement] = type(
    "dialog", (core.HTMLDialogElement,), {"name": "dialog"}
)


# legacy.
doctype: type[core.DocumentType] = type(
    "doctype", (core.DocumentType,), {"name": "doctype"}
)
comment: type[core.Comment] = type("comment", (core.Comment,), {"name": "comment"})


def create_element(name="custom_tag", *args, **kwargs) -> core.Element:
    """
    A method for creating custom tags

    tag name needs to be set due to custom tags with hyphens can't be classnames.
    i.e. hypenated tags <some-custom-tag></some-custom-tag>
    """
    # checks if already exists
    if name in core.html_tags:
        return globals()[name](*args, **kwargs)

    # NOTE: we care calling it custom_tag because it can't have hyphens
    custom_tag: type[core.Element] = type("custom_tag", (core.Element,), {"name": name})
    new_tag = custom_tag(*args, **kwargs)
    new_tag.name = name
    return new_tag
