<?php
$conexion = mysqli_connect("localhost", "app", "fixture-clave", "padron");

$id = $_GET['id'];
$resultado = mysqli_query($conexion, "SELECT * FROM usuarios WHERE id = " . $id);

$archivo = $_GET['archivo'];
system("cat /var/reportes/" . $archivo);

echo "Hola " . $_GET['nombre'];
