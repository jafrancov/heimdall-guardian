<?php
function traer($url, $host)
{
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    $a = file_get_contents("http://" . $host . "/datos");
    $b = Http::get($url);
}
