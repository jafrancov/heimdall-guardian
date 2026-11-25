<?php
function leer()
{
    $f = fopen("/etc/app/config.ini", "r");
    $c = file_get_contents("/etc/app/config.ini");
    readfile("/datos/ayuda.txt");
    unlink("/tmp/cache.lock");
}
