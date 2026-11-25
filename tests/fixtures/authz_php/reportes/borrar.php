<?php
$db->query("DELETE FROM reportes WHERE id = " . intval($_GET['id']));
echo "borrado";
