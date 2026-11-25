<?php
$carrito = json_decode($_COOKIE['carrito'], true);
$cache = unserialize(file_get_contents(__DIR__ . '/cache.bin'));
