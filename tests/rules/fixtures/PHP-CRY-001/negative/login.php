<?php
$hash = password_hash($password, PASSWORD_DEFAULT);
$etag = md5($contenido);
$huella = sha1_file($ruta);
