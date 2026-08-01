<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class VehicleLocation extends Model
{
    public $timestamps = false;

    protected $fillable = [
        'vehicle_id',
        'latitude',
        'longitude',
        'speed',
        'bearing',
        'geofence_zone',
        'position',
        'pinged_at',
    ];

    protected $casts = [
        'latitude' => 'double',
        'longitude' => 'double',
        'speed' => 'double',
        'bearing' => 'double',
        'pinged_at' => 'datetime',
    ];

    public function vehicle(): BelongsTo
    {
        return $this->belongsTo(Vehicle::class);
    }
}
