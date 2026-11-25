<?php
use Illuminate\Support\Facades\Route;

Route::get('/expedientes', [ExpedienteController::class, 'index']);
Route::post('/expedientes', [ExpedienteController::class, 'store']);

Route::middleware('throttle:60')->group(function () {
    Route::delete('/expedientes/{id}', [ExpedienteController::class, 'destroy']);
});
