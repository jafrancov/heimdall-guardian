<?php

use Illuminate\Support\Facades\Route;

Route::apiResource('predios', PredioController::class);
Route::middleware('auth:sanctum')->group(function () {
    Route::match(['put', 'patch'], '/usuarios/{id}', [UsuarioController::class, 'update']);
});
