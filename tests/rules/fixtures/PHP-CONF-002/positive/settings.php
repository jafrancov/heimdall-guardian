<?php
const PRODUCTION = False;  # change to true when deployed
define('IS_PRODUCTION', false);
define("PRODUCCION", 0);
const DEBUG = true;
define('APP_DEBUG', TRUE);
const DEBUG_MODE = 1;

if (!PRODUCTION) {
    ini_set('display_errors', 1);
}
