<?php

use Illuminate\Support\Facades\Route;
Route::post('posts', [PostController::class, 'store']);

