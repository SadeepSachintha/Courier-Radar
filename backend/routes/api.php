<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\TelemetryController;

Route::post('/telemetry', [TelemetryController::class, 'update']);
