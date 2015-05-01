import xml.etree.ElementTree as ElementTree

"""
Program copied from: 
http://stackoverflow.com/questions/2148119/how-to-convert-an-xml-string-to-a-dictionary-in-python 

Note that xmltodict and dicttoxml are python modules that can be imported:
https://pypi.python.org/pypi/xmltodict
https://pypi.python.org/pypi/dicttoxml

However as it appears these are very short utilities, they have been
captured here below from the stackoverflow listed above.  This delays needing
to incorporate the xml<-->dict utilities within Mantid while development is
proceding.

Note that these functions only work with one root element - examples below

Example xml:
<root>
    <sape>4139</sape>
    <jack>4098</jack>
    <guido>4127</guido>
</root>

Example dictionary:
some_dict={'root':{'sape': 4139, 'guido': 4127, 'jack': 4098}}


"""

def xmltodict(element):
    """
    Experience shows that the following isinstance() check crashes for some reason
    under RHEL 6.  This being the case, the test is made optional now
    """
    try:
        if not isinstance(element, ElementTree.Element):
            raise ValueError("must pass xml.etree.ElementTree.Element object")
    except:
        pass

    def xmltodict_handler(parent_element):
        result = dict()
        for element in parent_element:
            if len(element):
                obj = xmltodict_handler(element)
            else:
                obj = element.text

            if result.get(element.tag):
                if hasattr(result[element.tag], "append"):
                    result[element.tag].append(obj)
                else:
                    result[element.tag] = [result[element.tag], obj]
            else:
                result[element.tag] = obj
        return result

    return {element.tag: xmltodict_handler(element)}


def dicttoxml(element):
    if not isinstance(element, dict):
        raise ValueError("must pass dict type")
    if len(element) != 1:
        raise ValueError("dict must have exactly one root key")

    def dicttoxml_handler(result, key, value):
        if isinstance(value, list):
            for e in value:
                dicttoxml_handler(result, key, e)
        elif isinstance(value, basestring):
            elem = ElementTree.Element(key)
            elem.text = value
            result.append(elem)
        elif isinstance(value, int) or isinstance(value, float):
            elem = ElementTree.Element(key)
            elem.text = str(value)
            result.append(elem)
        elif value is None:
            result.append(ElementTree.Element(key))
        else:
            res = ElementTree.Element(key)
            for k, v in value.items():
                dicttoxml_handler(res, k, v)
            result.append(res)

    result = ElementTree.Element(element.keys()[0])
    for key, value in element[element.keys()[0]].items():
        dicttoxml_handler(result, key, value)
    return result

def xmlfiletodict(filename):
    return xmltodict(ElementTree.parse(filename).getroot())

def dicttoxmlfile(element, filename):
    ElementTree.ElementTree(dicttoxml(element)).write(filename)

def xmlstringtodict(xmlstring):
    return xmltodict(ElementTree.fromstring(xmlstring).getroot())

def dicttoxmlstring(element):
    return ElementTree.tostring(dicttoxml(element))