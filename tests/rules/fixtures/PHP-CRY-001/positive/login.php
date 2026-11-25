<?php
$hash = md5($password);
$otro = sha1($_POST['clave']);
$tercero = hash('md5', $contrasena);
