<?php
function leer($contenido, $ruta, $parser) {
    $a = simplexml_load_string($contenido);
    $b = simplexml_load_file($ruta, 'SimpleXMLElement', LIBXML_NOENT);
    $doc = new DOMDocument();
    $doc->loadXML($contenido, LIBXML_NOENT);
    $doc->load($ruta);
    $e = new SimpleXMLElement($contenido);
    xml_parse($parser, $contenido, true);
}
