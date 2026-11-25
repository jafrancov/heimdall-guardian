import json
import xml.etree.ElementTree as ET
from lxml import etree


def leer(request):
    a = etree.fromstring("<a><b/></a>")
    b = ET.fromstring('<root/>')
    c = json.loads(request.body)
    d = etree.parse("config/base.xml")
    return a, b, c, d
