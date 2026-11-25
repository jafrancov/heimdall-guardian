<?php
$carrito = unserialize($_COOKIE['carrito']);
$datos = base64_decode($_POST['datos']);
$objeto = unserialize($datos);
