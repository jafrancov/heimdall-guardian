<?php
echo "Hola " . $_GET['nombre'];
$mensaje = $_POST['mensaje'];
print($mensaje);

// A text/html header does not make the output safe.
header('Content-Type: text/html; charset=utf-8');
echo $_GET['titulo'];

function sin_cabecera() {
    // json_encode does not escape "<" and no JSON header was sent.
    echo json_encode(array('q' => $_GET['q']));
}
