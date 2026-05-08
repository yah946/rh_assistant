<?php

use App\Http\Controllers\API\AuthController;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;

Route::get('/user', function (Request $request) {
    return $request->user();
})->middleware('auth:sanctum');


Route::controller(AuthController::class)->group(function () {
    Route::post('register');
    Route::post('login');
    Route::middleware('auth:api')->group(function () {
        Route::post('logout');
        Route::post('refresh');
    });
});