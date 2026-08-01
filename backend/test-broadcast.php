<?php
require_once __DIR__.'/vendor/autoload.php';
$app = require_once __DIR__.'/bootstrap/app.php';
$kernel = $app->make(Illuminate\Contracts\Http\Kernel::class);
$kernel->bootstrap();

echo "Starting broadcast test...\n";
$t1 = microtime(true);
event(new \App\Events\VehicleLocationUpdated([
    'vehicle_id' => 'V-101',
    'latitude' => 6.9271,
    'longitude' => 79.8432,
    'speed' => 25.4,
    'bearing' => 120.0,
    'geofence_zone' => 'A',
    'timestamp' => time()
]));
$t2 = microtime(true);
echo "Event broadcast finished in " . ($t2 - $t1) . " seconds.\n";
