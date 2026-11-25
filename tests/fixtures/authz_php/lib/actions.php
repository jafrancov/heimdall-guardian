<?php
$db = new mysqli('localhost', 'u', 'p', 'd');
switch ($_POST['option']) {
    case 'list':
        $rows = $db->query("SELECT * FROM items");
        break;
    case 'save':
        $db->query("UPDATE items SET name = '" . $_POST['name'] . "' WHERE id = 1");
        break;
    case 'drop':
        $db->query("DELETE FROM items WHERE id = " . $_POST['id']);
        break;
}
