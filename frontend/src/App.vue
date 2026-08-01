<template>
  <div class="flex flex-col h-screen w-screen bg-slate-950 font-sans text-slate-100 overflow-hidden select-none">
    <!-- Header -->
    <header class="flex items-center justify-between px-6 py-4 bg-slate-900/80 border-b border-slate-800 z-10 glass">
      <div class="flex items-center space-x-3">
        <div class="w-8 h-8 rounded-lg bg-sky-500 flex items-center justify-center shadow-lg shadow-sky-500/30 animate-pulse">
          <svg class="w-5 h-5 text-slate-950" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        </div>
        <div>
          <h1 class="text-lg font-black tracking-wider uppercase text-white leading-none">Courier Radar</h1>
          <span class="text-[10px] text-sky-400 font-mono tracking-widest uppercase">Live Fleet Operations Center</span>
        </div>
      </div>

      <!-- Network status badge -->
      <div class="flex items-center space-x-4">
        <div class="flex items-center space-x-2 px-3 py-1.5 rounded-full text-xs font-semibold glass">
          <span :class="['w-2.5 h-2.5 rounded-full inline-block animate-ping', isConnected ? 'bg-emerald-400' : 'bg-amber-500']"></span>
          <span :class="['w-2.5 h-2.5 rounded-full inline-block absolute', isConnected ? 'bg-emerald-500' : 'bg-amber-500']"></span>
          <span class="text-xs font-mono ml-2">{{ isConnected ? 'REVERB LIVE' : 'CONNECTING...' }}</span>
        </div>
        <div class="text-[11px] text-slate-400 font-mono hidden md:block">
          System Time: <span class="text-white">{{ currentTime }}</span>
        </div>
      </div>
    </header>

    <!-- Main Container -->
    <div class="flex flex-1 relative overflow-hidden">
      <!-- Left Sidebar: Stats & Vehicle List -->
      <aside class="w-80 h-full flex flex-col border-r border-slate-800 bg-slate-950/90 z-10 glass transition-all duration-300 absolute md:relative -translate-x-full md:translate-x-0">
        <!-- Stats Summary Grid -->
        <div class="grid grid-cols-2 gap-2 p-4 border-b border-slate-800">
          <div class="p-3 bg-slate-900/60 rounded-lg border border-slate-800/80">
            <div class="text-[10px] font-semibold text-slate-400 uppercase font-mono">Total Assets</div>
            <div class="text-2xl font-bold mt-1 text-white">{{ stats.total }}</div>
          </div>
          <div class="p-3 bg-slate-900/60 rounded-lg border border-slate-800/80">
            <div class="text-[10px] font-semibold text-emerald-400 uppercase font-mono">Moving</div>
            <div class="text-2xl font-bold mt-1 text-emerald-400">{{ stats.moving }}</div>
          </div>
          <div class="p-3 bg-slate-900/60 rounded-lg border border-slate-800/80">
            <div class="text-[10px] font-semibold text-amber-500 uppercase font-mono">Idle</div>
            <div class="text-2xl font-bold mt-1 text-amber-500">{{ stats.idle }}</div>
          </div>
          <div class="p-3 bg-slate-900/60 rounded-lg border border-slate-800/80">
            <div class="text-[10px] font-semibold text-rose-500 uppercase font-mono">Geofenced</div>
            <div class="text-2xl font-bold mt-1 text-rose-500 animate-pulse" v-if="stats.geofences > 0">{{ stats.geofences }}</div>
            <div class="text-2xl font-bold mt-1 text-slate-500" v-else>0</div>
          </div>
        </div>

        <!-- Vehicle List -->
        <div class="flex-1 flex flex-col min-h-0">
          <div class="px-4 py-2 border-b border-slate-800 flex items-center justify-between bg-slate-900/20">
            <span class="text-xs font-bold text-slate-400 font-mono uppercase">Fleet Status Directory</span>
            <span class="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 font-mono">{{ vehicleList.length }} online</span>
          </div>

          <div class="flex-1 overflow-y-auto custom-scrollbar p-3 space-y-2">
            <div 
              v-for="vehicle in sortedVehicles" 
              :key="vehicle.vehicle_id"
              @click="focusVehicle(vehicle)"
              class="p-3 rounded-lg border border-slate-850 hover:border-sky-500/50 bg-slate-900/40 hover:bg-slate-900/80 transition cursor-pointer relative overflow-hidden group"
            >
              <!-- Indicator colored border -->
              <div :class="['absolute left-0 top-0 bottom-0 w-1.5', getStatusColor(vehicle.status)]"></div>
              
              <div class="pl-2">
                <div class="flex justify-between items-start">
                  <span class="font-bold text-sm text-slate-200 group-hover:text-white transition">{{ vehicle.vehicle_name }}</span>
                  <span class="text-[10px] font-mono text-slate-500 px-1 py-0.5 bg-slate-950 rounded">{{ vehicle.vehicle_id }}</span>
                </div>
                
                <div class="flex justify-between items-center mt-2 text-xs">
                  <div class="flex items-center space-x-1.5 text-slate-400">
                    <span class="capitalize">{{ vehicle.vehicle_type }}</span>
                    <span>•</span>
                    <span :class="getStatusTextColor(vehicle.status)">{{ vehicle.status }}</span>
                  </div>
                  <div class="font-mono text-white text-right">
                    <span class="font-semibold">{{ vehicle.speed }}</span> <span class="text-[10px] text-slate-400">km/h</span>
                  </div>
                </div>

                <div v-if="vehicle.geofence_zone" class="mt-2 text-[10px] flex items-center space-x-1 text-rose-400 bg-rose-950/40 border border-rose-800/40 px-2 py-0.5 rounded font-mono">
                  <span>📍 Inside Galle Face Green</span>
                </div>
              </div>
            </div>

            <div v-if="vehicleList.length === 0" class="h-40 flex flex-col items-center justify-center text-slate-500 space-y-2 border border-dashed border-slate-800 rounded-lg">
              <svg class="w-8 h-8 opacity-40 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <div class="text-xs font-mono">WAITING FOR TELEMETRY...</div>
            </div>
          </div>
        </div>
      </aside>

      <!-- Center Map Viewport -->
      <main class="flex-1 h-full relative">
        <div id="map-container" class="w-full h-full"></div>

        <!-- Custom overlay for Map search/loading status -->
        <div v-if="!isConnected" class="absolute inset-0 bg-slate-950/40 backdrop-blur-[2px] flex items-center justify-center z-[1000] pointer-events-none">
          <div class="px-4 py-2.5 rounded-lg border border-slate-800 bg-slate-900/90 text-sm font-semibold tracking-wider text-sky-400 shadow-2xl flex items-center space-x-3">
            <svg class="animate-spin h-4 w-4 text-sky-400" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span>CONNECTING STREAM PIPELINE...</span>
          </div>
        </div>
      </main>

      <!-- Right Sidebar: Live Alerts & Feed -->
      <aside class="w-80 h-full border-l border-slate-800 bg-slate-950/90 flex flex-col z-10 glass hidden lg:flex">
        <div class="p-4 border-b border-slate-800 bg-slate-900/20 flex items-center justify-between">
          <span class="text-xs font-bold text-slate-400 font-mono uppercase">System Log & alerts</span>
          <button @click="clearAlerts" class="text-[10px] text-slate-500 hover:text-white transition font-mono">CLEAR</button>
        </div>

        <!-- System alerts stream -->
        <div class="flex-1 overflow-y-auto custom-scrollbar p-3 space-y-2">
          <div 
            v-for="alert in alerts" 
            :key="alert.id"
            :class="['p-3 rounded-lg border text-xs leading-relaxed transition-all duration-300 font-mono', getAlertStyle(alert.type)]"
          >
            <div class="flex justify-between items-center mb-1 text-[10px] text-slate-400">
              <span class="font-bold">{{ alert.vehicle_id }}</span>
              <span>{{ alert.time }}</span>
            </div>
            <div>{{ alert.message }}</div>
          </div>

          <div v-if="alerts.length === 0" class="h-full flex flex-col items-center justify-center text-slate-600 font-mono text-[11px] p-6 text-center">
            <div>NO RECENT TELEMETRY ALERTS</div>
            <div class="text-[9px] mt-1 opacity-50">Geofence and status events will feed here</div>
          </div>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import L from 'leaflet'
import { useFleetStore } from './store/fleet'

const fleetStore = useFleetStore()
const map = ref(null)
const markers = {}
const currentTime = ref(new Date().toLocaleTimeString())

// Fetch reactive properties from Pinia
const isConnected = computed(() => fleetStore.isConnected)
const vehicleList = computed(() => fleetStore.vehicleList)
const stats = computed(() => fleetStore.stats)
const alerts = computed(() => fleetStore.alerts)

// Sort vehicles so active ones show on top
const sortedVehicles = computed(() => {
  return [...vehicleList.value].sort((a, b) => {
    if (a.status === 'Offline') return 1
    if (b.status === 'Offline') return -1
    return a.vehicle_id.localeCompare(b.vehicle_id)
  })
})

// Initialize WebSockets and clock
onMounted(() => {
  fleetStore.initWebSockets()

  // Start checking for offline vehicles
  setInterval(() => {
    fleetStore.checkOfflineVehicles()
  }, 3000)

  // Update clock
  setInterval(() => {
    currentTime.value = new Date().toLocaleTimeString()
  }, 1000)

  // Map Initialization
  map.value = L.map('map-container', {
    center: [6.925, 79.855], // Colombo
    zoom: 14,
    zoomControl: false,
    attributionControl: false
  })

  // CartoDB Dark Matter Tiles
  L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    maxZoom: 20
  }).addTo(map.value)

  // Zoom controls
  L.control.zoom({ position: 'topright' }).addTo(map.value)

  // Draw Geofence Boundary
  // Colombo Galle Face Green coordinate bounding box
  const geofenceRect = L.rectangle([[6.9240, 79.8400], [6.9300, 79.8460]], {
    color: '#ef4444',
    weight: 2,
    fillColor: '#ef4444',
    fillOpacity: 0.08,
    dashArray: '5, 8'
  }).addTo(map.value)

  geofenceRect.bindTooltip('Galle Face Green Delivery Zone (A)', {
    permanent: true,
    direction: 'center',
    className: 'geofence-tooltip'
  })
})

// Focus the viewport on target vehicle marker
const focusVehicle = (v) => {
  if (v.status === 'Offline') return
  if (map.value) {
    map.value.flyTo([v.latitude, v.longitude], 16, { duration: 1.2 })
    if (markers[v.vehicle_id]) {
      markers[v.vehicle_id].openPopup()
    }
  }
}

// Map styles matching status
const getStatusColor = (status) => {
  switch (status) {
    case 'Moving': return 'bg-emerald-500'
    case 'Idle': return 'bg-amber-500'
    case 'Offline': return 'bg-slate-600'
    default: return 'bg-slate-600'
  }
}

const getStatusTextColor = (status) => {
  switch (status) {
    case 'Moving': return 'text-emerald-400 font-semibold'
    case 'Idle': return 'text-amber-400'
    case 'Offline': return 'text-slate-500'
    default: return 'text-slate-500'
  }
}

// Alert styles
const getAlertStyle = (type) => {
  switch (type) {
    case 'entry': return 'bg-rose-950/20 border-rose-900/40 text-rose-300'
    case 'exit': return 'bg-sky-950/20 border-sky-900/40 text-sky-300'
    case 'offline': return 'bg-slate-900/60 border-slate-800 text-slate-400'
    default: return 'bg-slate-900 border-slate-800 text-slate-200'
  }
}

const clearAlerts = () => {
  fleetStore.alerts = []
}

// Watch vehicles list and update markers
watch(vehicleList, (newVehicles) => {
  if (!map.value) return

  newVehicles.forEach((v) => {
    const { vehicle_id, latitude, longitude, bearing, status, vehicle_name, vehicle_type, speed } = v

    // Marker styling configuration
    let colorClass = 'bg-emerald-500 text-emerald-950 shadow-emerald-500/20'
    if (status === 'Idle') {
      colorClass = 'bg-amber-500 text-amber-950 shadow-amber-500/20'
    } else if (status === 'Offline') {
      colorClass = 'bg-slate-600 text-slate-200 shadow-slate-600/10'
    }

    const iconHtml = `
      <div class="relative flex items-center justify-center rounded-full w-8 h-8 shadow-xl border border-white/20 ${colorClass} vehicle-marker-icon" style="transform: rotate(${bearing}deg);">
        <!-- Direction Arrow -->
        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2L4.5 20.29l.71.71L12 18l6.79 3 .71-.71z"/>
        </svg>
      </div>
    `

    const customIcon = L.divIcon({
      html: iconHtml,
      className: 'bg-transparent',
      iconSize: [32, 32],
      iconAnchor: [16, 16]
    })

    if (markers[vehicle_id]) {
      // Smoothly reposition marker
      markers[vehicle_id].setLatLng([latitude, longitude])
      markers[vehicle_id].setIcon(customIcon)
      
      // Update pop up text contents
      markers[vehicle_id].setPopupContent(`
        <div class="text-slate-900 font-sans p-1 text-left">
          <div class="font-bold border-b border-slate-200 pb-1 text-sm">${vehicle_name}</div>
          <div class="text-[10px] text-slate-500 mt-1 font-mono">ID: ${vehicle_id}</div>
          <div class="text-xs mt-1">Status: <b class="${status === 'Moving' ? 'text-emerald-600' : 'text-amber-600'}">${status}</b></div>
          <div class="text-xs">Speed: <b>${speed} km/h</b></div>
          <div class="text-xs">Type: <span class="capitalize">${vehicle_type}</span></div>
        </div>
      `)
    } else {
      // New vehicle marker registration
      const marker = L.marker([latitude, longitude], { icon: customIcon })
        .addTo(map.value)
        .bindPopup(`
          <div class="text-slate-900 font-sans p-1 text-left">
            <div class="font-bold border-b border-slate-200 pb-1 text-sm">${vehicle_name}</div>
            <div class="text-[10px] text-slate-500 mt-1 font-mono">ID: ${vehicle_id}</div>
            <div class="text-xs mt-1">Status: <b class="${status === 'Moving' ? 'text-emerald-600' : 'text-amber-600'}">${status}</b></div>
            <div class="text-xs">Speed: <b>${speed} km/h</b></div>
            <div class="text-xs">Type: <span class="capitalize">${vehicle_type}</span></div>
          </div>
        `)
      
      markers[vehicle_id] = marker
    }
  })
}, { deep: true })
</script>

<style>
/* Adjust Popup Styling to blend with Tailwind theme */
.leaflet-popup-content-wrapper {
  background: rgba(255, 255, 255, 0.95) !important;
  border-radius: 8px !important;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3), 0 4px 6px -2px rgba(0, 0, 0, 0.05) !important;
}

.leaflet-popup-tip {
  background: rgba(255, 255, 255, 0.95) !important;
}

.geofence-tooltip {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  color: rgba(239, 68, 68, 0.8) !important;
  font-weight: 800 !important;
  font-family: monospace !important;
  font-size: 11px !important;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}
</style>
