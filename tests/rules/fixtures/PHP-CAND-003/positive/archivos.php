<?php
function leer($ruta, $nombre)
{
    $f = fopen($ruta, "r");
    $c = file_get_contents($ruta);
    readfile("/datos/" . $nombre);
    unlink($ruta);
}
