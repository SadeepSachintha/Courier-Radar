<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Vehicle extends Model
{
    protected $keyType = 'string';
    public $incrementing = false;

    protected $fillable = [
        'id',
        'name',
        'type',
        'status',
    ];

    public function locations(): HasMany
    {
        return $this->hasMany(VehicleLocation::class);
    }
}
