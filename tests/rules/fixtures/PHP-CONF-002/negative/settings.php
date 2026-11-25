<?php
// The environment comes from the server.
define('PRODUCTION', getenv('APP_ENV') === 'production');
const DEBUG = false;
define('APP_DEBUG', false);
const PRODUCTION = true;
const DEBUG_SQL = true;
// $debug = true is a local variable, not a deployment flag.
function trace($debug = true) {
    return $debug;
}
