<?php
$id = $_POST["id"];
mysqli_query($db, "DELETE FROM t WHERE id=$id");
echo "ok";
