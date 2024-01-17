from bs4 import BeautifulSoup, PageElement, Tag, NavigableString

def convertNodeAttrs(node: Tag):
    ret = []
    for attr in node.attrs:
        value = node.attrs[attr]

        if isinstance(value, list):
            value = " ".join(value)

        ret.append(
            f"'{attr}': '{value}'"
            # if ('-' in attr or ":" in attr) else
            # f'_{attr}="{value}"'   
        )
    return "**{" + ", ".join(ret) + "}"

def convertName(name: str):
    if "-" in name:
        return f'create_element("{name}")'
    else:
        return name

def convertNodes(nodes: list[PageElement]):
    ret = []
    for child in nodes:
        if isinstance(child, Tag):
            name = convertName(child.name)
            children = list(child.children)

            content = convertNodes(children) if children else ""
            attrs = convertNodeAttrs(child) if child.attrs else ""

            if content and attrs:
                content = content + ", "

            ret.append(f"{name}({ content }{ attrs })")
        elif isinstance(child, NavigableString):
            child = " ".join(child.stripped_strings).strip()
            if child:
                if "\n" in child:
                    ret.append(f'`{child}`')
                else:
                    ret.append(f'"{child}"')
    return ", ".join(ret)

def HtmlToPy(html):
    soup = BeautifulSoup(html, features="html.parser")
    return convertNodes(soup.children)

# with open("C:/Users/HP/Downloads/web-builders/VvvebJs-gui/libs/builder/gui.js", "a") as d:
#     d.write(HtmlToPy(html))