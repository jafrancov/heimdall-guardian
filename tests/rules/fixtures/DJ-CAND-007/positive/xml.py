from lxml import etree
import lxml.etree
import xml.dom.minidom
import xml.sax
import xml.etree.ElementTree as ET


def leer(request, ruta):
    a = lxml.etree.fromstring(request.body)
    b = lxml.etree.parse(ruta)
    c = lxml.etree.XML(request.body)
    d = etree.fromstring(request.body)
    e = etree.parse(ruta)
    f = etree.XML(request.body)
    g = xml.dom.minidom.parseString(request.body)
    h = xml.dom.minidom.parse(ruta)
    xml.sax.parseString(request.body, handler)
    xml.sax.parse(ruta, handler)
    i = ET.fromstring(request.body)
    j = ET.parse(ruta)
    return a, b, c, d, e, f, g, h, i, j
