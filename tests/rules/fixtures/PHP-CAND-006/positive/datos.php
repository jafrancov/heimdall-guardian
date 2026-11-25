<?php
function cargar($raw, $texto) {
    $a = unserialize($raw);
    $b = unserialize($_COOKIE['perfil'], ['allowed_classes' => true]);
    $c = yaml_parse($texto);
    return [$a, $b, $c];
}
