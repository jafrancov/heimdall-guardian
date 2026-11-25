<?php
use Illuminate\Support\Facades\Route;

Route::middleware('auth')->group(function () {
    Route::get('/expedientes', [ExpedienteController::class, 'index']);
    Route::post('/expedientes', [ExpedienteController::class, 'store']);
});

Route::middleware(['web', 'auth:sanctum'])->group(function () {
    Route::delete('/expedientes/{id}', [ExpedienteController::class, 'destroy']);
});

Route::group(['middleware' => 'auth'], function () {
    Route::get('/pagos', [PagoController::class, 'index']);
});

Route::get('/perfil', [PerfilController::class, 'show'])->middleware('auth');
