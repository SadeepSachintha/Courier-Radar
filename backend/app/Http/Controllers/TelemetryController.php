<?php

namespace App\Http\Controllers;

use App\Models\Vehicle;
use App\Models\VehicleLocation;
use App\Events\VehicleLocationUpdated;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Carbon\Carbon;

class TelemetryController extends Controller
{
    public function update(Request $request)
    {
        $data = $request->validate([
            'vehicle_id' => 'required|string',
            'vehicle_name' => 'required|string',
            'vehicle_type' => 'required|string',
            'latitude' => 'required|numeric',
            'longitude' => 'required|numeric',
            'speed' => 'required|numeric',
            'bearing' => 'required|numeric',
            'status' => 'required|string',
            'geofence_zone' => 'nullable|string',
            'timestamp' => 'required|numeric',
        ]);

        // Find or create vehicle profile
        $vehicle = Vehicle::updateOrCreate(
            ['id' => $data['vehicle_id']],
            [
                'name' => $data['vehicle_name'],
                'type' => $data['vehicle_type'],
                'status' => $data['status'],
            ]
        );

        // Save historical position ping in PostGIS
        VehicleLocation::create([
            'vehicle_id' => $data['vehicle_id'],
            'latitude' => $data['latitude'],
            'longitude' => $data['longitude'],
            'speed' => $data['speed'],
            'bearing' => $data['bearing'],
            'geofence_zone' => $data['geofence_zone'],
            'position' => DB::raw("ST_GeomFromText('POINT(" . $data['longitude'] . " " . $data['latitude'] . ")', 4326)"),
            'pinged_at' => Carbon::createFromTimestamp($data['timestamp']),
        ]);

        // Dispatch real-time WebSocket broadcast event
        event(new VehicleLocationUpdated($data));

        return response()->json([
            'status' => 'success',
            'message' => 'Telemetry logged and broadcasted'
        ], 200);
    }
}
