<?php
function env_or($name, $fallback) {
    $value = getenv($name);
    return $value === false ? $fallback : $value;
}

define('DB_HOST', env_or('APP_DB_HOST', 'localhost'));
$timeout = env_or('APP_TIMEOUT', '30');
