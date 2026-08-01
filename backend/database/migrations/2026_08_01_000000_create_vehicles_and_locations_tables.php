<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;
use Illuminate\Support\Facades\DB;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        // Enable PostGIS extension (required for geospatial types)
        DB::statement('CREATE EXTENSION IF NOT EXISTS postgis');

        Schema::create('vehicles', function (Blueprint $table) {
            $table->string('id')->primary(); // V-101, etc.
            $table->string('name');
            $table->string('type'); // tuktuk, bike, etc.
            $table->string('status'); // Moving, Idle, Offline
            $table->timestamps();
        });

        Schema::create('vehicle_locations', function (Blueprint $table) {
            $table->id();
            $table->string('vehicle_id');
            $table->double('latitude');
            $table->double('longitude');
            $table->decimal('speed', 8, 2)->default(0.00);
            $table->decimal('bearing', 8, 2)->default(0.00);
            $table->string('geofence_zone')->nullable();
            
            // PostGIS Point geometry column (SRID 4326 is standard GPS coordinates)
            $table->geometry('position', subtype: 'point', srid: 4326);
            
            $table->timestamp('pinged_at');
            $table->timestamp('created_at')->useCurrent();

            $table->foreign('vehicle_id')->references('id')->on('vehicles')->onDelete('cascade');
        });

        // Add spatial index for fast distance queries
        DB::statement('CREATE INDEX vehicle_locations_position_spatial_index ON vehicle_locations USING gist(position)');
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('vehicle_locations');
        Schema::dropIfExists('vehicles');
    }
};
