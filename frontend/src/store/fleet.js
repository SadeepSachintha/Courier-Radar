import { defineStore } from 'pinia'
import Echo from 'laravel-echo'
import Pusher from 'pusher-js'

export const useFleetStore = defineStore('fleet', {
  state: () => ({
    vehicles: {},
    alerts: [],
    isConnected: false,
    echo: null
  }),
  getters: {
    vehicleList: (state) => Object.values(state.vehicles),
    stats: (state) => {
      const list = Object.values(state.vehicles)
      const total = list.length
      const moving = list.filter(v => v.status === 'Moving').length
      const idle = list.filter(v => v.status === 'Idle').length
      const offline = list.filter(v => v.status === 'Offline').length
      const geofences = list.filter(v => v.geofence_zone).length
      return { total, moving, idle, offline, geofences }
    }
  },
  actions: {
    initWebSockets() {
      if (this.echo) return

      window.Pusher = Pusher

      // Connect to Laravel Reverb WebSocket Server
      this.echo = new Echo({
        broadcaster: 'reverb',
        key: 'courierkey',
        wsHost: window.location.hostname,
        wsPort: 8080,
        wssPort: 8080,
        forceTLS: false,
        enabledTransports: ['ws', 'wss'],
        disableStats: true
      })

      // Bind connection status events
      this.echo.connector.pusher.connection.bind('state_change', (states) => {
        this.isConnected = states.current === 'connected'
      })

      // Listen on the public telemetry channel
      this.echo.channel('telemetry')
        .listen('.VehicleLocationUpdated', (data) => {
          this.updateVehicle(data)
        })

      // Connection recovery check
      setInterval(() => {
        if (this.echo && this.echo.connector.pusher.connection.state === 'disconnected') {
          console.log('Reconnecting to WebSockets...')
          this.echo.connector.pusher.connection.connect()
        }
      }, 5000)
    },
    updateVehicle(data) {
      const now = Date.now()
      const vehicleId = data.vehicle_id
      const prevVehicle = this.vehicles[vehicleId]

      // Geofence alerts
      if (data.geofence_zone && (!prevVehicle || !prevVehicle.geofence_zone)) {
        this.addAlert({
          id: `${now}-${vehicleId}`,
          vehicle_id: vehicleId,
          vehicle_name: data.vehicle_name,
          type: 'entry',
          message: `🚨 ${data.vehicle_name} entered ${data.geofence_zone}`,
          time: new Date().toLocaleTimeString()
        })
      } else if (!data.geofence_zone && prevVehicle && prevVehicle.geofence_zone) {
        this.addAlert({
          id: `${now}-${vehicleId}`,
          vehicle_id: vehicleId,
          vehicle_name: data.vehicle_name,
          type: 'exit',
          message: `ℹ️ ${data.vehicle_name} left ${prevVehicle.geofence_zone}`,
          time: new Date().toLocaleTimeString()
        })
      }

      // Update vehicle status in state
      this.vehicles[vehicleId] = {
        ...data,
        lastSeen: now
      }
    },
    addAlert(alert) {
      this.alerts.unshift(alert)
      if (this.alerts.length > 30) {
        this.alerts.pop()
      }
    },
    checkOfflineVehicles() {
      const now = Date.now()
      Object.keys(this.vehicles).forEach((id) => {
        const v = this.vehicles[id]
        if (v.status !== 'Offline' && (now - v.lastSeen) > 8000) {
          v.status = 'Offline'
          v.speed = 0
          this.addAlert({
            id: `${now}-${id}`,
            vehicle_id: id,
            vehicle_name: v.vehicle_name,
            type: 'offline',
            message: `⚠️ Connection lost with ${v.vehicle_name}`,
            time: new Date().toLocaleTimeString()
          })
        }
      })
    }
  }
})
