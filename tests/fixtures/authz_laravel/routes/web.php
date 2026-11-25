<?php

use Illuminate\Support\Facades\Route;

Route::get('/', function () {
    return view('welcome');
});
Route::post('/login', [SesionController::class, 'entrar']);

Route::middleware(['web', 'auth'])->prefix('expedientes')->group(function () {
    Route::get('/', [ExpedienteController::class, 'index']);
    Route::post('/', [ExpedienteController::class, 'store']);

    Route::prefix('anexos')->group(function () {
        Route::delete('/{id}', [AnexoController::class, 'destroy']);
    });
});

Route::group(['prefix' => 'reportes', 'middleware' => 'throttle:60'], function () {
    Route::get('/mensual', 'ReporteController@mensual');
    Route::get('/anual', 'ReporteController@anual')->middleware('auth');
});

// Route::get('/comentada', 'X@y');
Route::put('/perfil', [PerfilController::class, 'update'])->middleware('auth:sanctum');
Route::get('/tablero', [TableroController::class, 'index']);
