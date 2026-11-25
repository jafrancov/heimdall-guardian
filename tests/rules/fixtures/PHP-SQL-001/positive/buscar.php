<?php
$id = $_GET['id'];
$resultado = mysqli_query($conexion, "SELECT * FROM usuarios WHERE id = " . $id);
$filas = $pdo->query("SELECT * FROM pagos WHERE folio = '" . $_POST['folio'] . "'");
pg_query($db, "SELECT * FROM predios WHERE clave = '{$_REQUEST['clave']}'");
