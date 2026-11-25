<?php
// Original name used directly in the destination.
function save_direct() {
    move_uploaded_file($_FILES['doc']['tmp_name'], '/srv/files/' . $_FILES['doc']['name']);
}

// Through an intermediate variable; basename() does not make the name safe.
function save_alias() {
    $f = $_FILES['doc'];
    $dest = '/srv/files/' . basename($f['name']);
    move_uploaded_file($f['tmp_name'], $dest);
}

// The upload field name is used as the folder.
function save_by_field() {
    foreach ($_FILES as $key => $file) {
        move_uploaded_file($file['tmp_name'], "/srv/files/$key/" . uniqid());
    }
}

// A form field chooses the folder.
function save_in_chosen_folder() {
    $dir = $_POST['folder'];
    move_uploaded_file($_FILES['doc']['tmp_name'], '/srv/files/' . $dir . '/' . uniqid() . '.dat');
}

// Generated name but the extension comes from the client and is never checked.
function save_with_client_extension() {
    $f = $_FILES['doc'];
    $ext = pathinfo($f['name'], PATHINFO_EXTENSION);
    move_uploaded_file($f['tmp_name'], '/srv/files/' . uniqid() . '.' . $ext);
}

// Backup copy and rename keep the client name.
function keep_backup() {
    $f = $_FILES['doc'];
    $target = '/srv/files/' . basename($f['name']);
    copy($target, $target . '.bak');
    rename('/srv/tmp/last', '/srv/files/' . $f['name']);
}
