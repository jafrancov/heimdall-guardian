<?php
function cargar($raw) {
    $a = unserialize('a:1:{i:0;s:1:"x";}');
    $b = json_decode($raw, true);
    $c = yaml_parse('clave: valor');
    return [$a, $b, $c];
}
