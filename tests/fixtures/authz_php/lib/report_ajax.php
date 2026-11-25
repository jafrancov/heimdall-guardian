<?php
require_once __DIR__ . '/verification_model.php';
$model = new VerificationModel();
$db->query("DELETE FROM reports WHERE id = " . $_POST['id']);
echo 'ok';
