<?php
function traer()
{
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, "https://api.example.com/datos");
    curl_setopt($ch, CURLOPT_TIMEOUT, 5);
    $b = Http::get("https://api.example.com/estado");
}
