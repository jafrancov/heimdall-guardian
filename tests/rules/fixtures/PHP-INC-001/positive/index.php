<?php
$pagina = $_GET['pagina'];
include $pagina . ".php";
require_once("modulos/" . $modulo);

// A fixed base but a variable part: still reported.
$libpath = dirname(__FILE__);
require_once $libpath . '/' . $module . '.php';
function from_param($file) {
    $dir = dirname(__FILE__);
    include $dir . $file;
    include $file;
}
// The base comes from request data.
$tpl = $_GET['dir'];
require $tpl . '/index.php';
// A safe base joined with request data, or a request-data base.
$dir1 = dirname(realpath(__FILE__)) . $_GET['p'];
require $dir1;
$dir2 = $_GET['d'];
require $dir2 . '/x.php';
