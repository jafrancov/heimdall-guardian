<?php
$id = intval($_GET['id']);
$resultado = mysqli_query($conexion, "SELECT * FROM usuarios WHERE id = " . $id);
$consulta = $pdo->prepare("SELECT * FROM pagos WHERE folio = ?");
$consulta->execute([$_POST['folio']]);
$todos = $pdo->query("SELECT * FROM pagos");
