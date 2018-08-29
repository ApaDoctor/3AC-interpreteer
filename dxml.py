import xml.etree.ElementTree as ElementTree
from copy import copy

"""
Converts xml to python dict.
"""


def dictify(r, root=True):
    """
    Recursive function used to convert xml to python file.
    :param r: root of xml tree
    :param root: is it root node
    :return: dict representation of xml
    """
    if root:
        return {r.tag: dictify(r, False)}
    d = copy(r.attrib)
    if r.text and r.text.replace(" ", "").replace("\n", ""):
        d["__val__"] = r.text
    for x in r.findall("./*"):
        if x.tag not in d:
            d[x.tag] = []
        d[x.tag].append(dictify(x, False))
    return d


if __name__ == "__main__":
    tree = ElementTree.parse('file.xml')
    root = tree.getroot()
    xmldict = dictify(root)

    # print(xmldict)
    # print(len(xmldict["program"]["instruction"]))

    for x in xmldict["program"]["instruction"]:
        print(x["order"])
