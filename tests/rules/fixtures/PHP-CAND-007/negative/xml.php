<?php
function leer($contenido, $parser) {
    $a = simplexml_load_string('<a><b/></a>');
    $doc = new DOMDocument();
    $doc->loadXML('<a/>');
    $doc->load('/etc/app/config.xml');
    $json = json_decode($contenido, true);
    $e = new SimpleXMLElement('<root/>');
}
