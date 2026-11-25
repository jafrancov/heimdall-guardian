<?php
include "cabecera.php";
require_once __DIR__ . '/config.php';
require 'vendor/autoload.php';

// Fixed base directory plus literals.
$libpath = dirname(__FILE__);
require_once $libpath . '/lib/helpers.php';
$base = realpath(dirname(__FILE__) . '/..');
include $base . '/shared/' . 'menu.php';
$root = __DIR__;
require $root;
$fixed = 'modules/core';
include_once $fixed . '/boot.php';
$app = APP_ROOT . '/app';
require_once($app . '/start.php');
require_once ROOT_DIR . '/lib/model.php';

function load_view() {
    $dir = dirname(__FILE__, 2);
    include $dir . "/views/main.php";
}

// Nested dirname() calls.
$top = dirname(dirname(__FILE__));
require_once $top . '/settings.php';
$up = dirname(__DIR__, 2);
include $up . '/boot.php';

// Any nesting of dirname() and realpath() around the magic constants.
$d1 = dirname(realpath(__FILE__));
require_once $d1 . '/controller.php';
$d2 = dirname(realpath(__DIR__));
require_once $d2 . "/x.php";
$d3 = realpath(__DIR__);
include $d3 . '/../settings.php';
$d4 = dirname(realpath(__FILE__), 2);
require $d4 . "/lib/boot.php";
