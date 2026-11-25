<?php
// The stored name is generated on the server.
function save_generated() {
    $name = bin2hex(random_bytes(8)) . '.dat';
    move_uploaded_file($_FILES['doc']['tmp_name'], '/srv/files/' . $name);
}

// The upload name is checked against an allowlist and the code exits otherwise.
function save_allowed_names() {
    $allowed = array('report.xlsx', 'sales.xlsx');
    if (!isset($_FILES['doc']['name']) || !in_array($_FILES['doc']['name'], $allowed, true)) {
        exit;
    }
    $f = $_FILES['doc'];
    if (move_uploaded_file($f['tmp_name'], '/srv/files/' . $f['name'])) {
        echo 'ok';
    }
}

// The extension is checked against an allowlist before the move.
function save_checked_extension() {
    $ext = strtolower(pathinfo($_FILES['doc']['name'], PATHINFO_EXTENSION));
    if (!in_array($ext, array('jpg', 'png'), true)) {
        return false;
    }
    return move_uploaded_file($_FILES['doc']['tmp_name'], '/srv/files/' . uniqid() . '.' . $ext);
}

// An anchored pattern on the extension guards the move.
function save_pattern_extension() {
    $f = $_FILES['doc'];
    $ext = pathinfo($f['name'], PATHINFO_EXTENSION);
    if (preg_match('/^(pdf|png)$/D', $ext)) {
        move_uploaded_file($f['tmp_name'], '/srv/files/' . uniqid() . '.' . $ext);
    }
}

// The folder comes from the request but it is chosen from a fixed list.
function save_in_listed_folder() {
    $dir = $_POST['folder'];
    if (!in_array($dir, array('invoices', 'receipts'), true)) {
        exit;
    }
    move_uploaded_file($_FILES['doc']['tmp_name'], '/srv/files/' . $dir . '/' . uniqid() . '.dat');
}

// The folder is resolved and must stay inside the upload root.
function save_inside_root($sub) {
    $root = realpath('/srv/files');
    $real = realpath($root . '/' . $_POST['folder']);
    if ($real === false || strpos($real . '/', $root . '/') !== 0) {
        return false;
    }
    return move_uploaded_file($_FILES['doc']['tmp_name'], $real . '/' . uniqid() . '.dat');
}

// Numeric identifiers only.
function save_by_id() {
    $id = (int) $_POST['id'];
    move_uploaded_file($_FILES['doc']['tmp_name'], '/srv/files/' . $id . '.dat');
}
