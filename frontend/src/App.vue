<template>
  <div id="vue-app">
    <h1 class="icons">Snaptastic</h1>
    <p>{{ statusText }}</p>
    <button @click="connected ? disconnect() : connect()" :disabled="busy">
      {{ connected ? 'Disconnect' : 'Connect camera' }}
    </button>
    <img v-if="connected" class="live" :src="liveUrl" alt="Live view" />
    <button v-if="connected" class="shutter" @click="shoot" :disabled="shooting">
      {{ shooting ? 'Taking photo...' : 'Shutter' }}
    </button>
    <img v-if="lastPhoto" class="photo" :src="`${API}/photos/${lastPhoto}`" alt="Last photo" />
    <!-- <video id="video" ref="videoRef" muted autoplay></video>
    <button @click="enabled = !enabled">
      {{ enabled ? 'Stop' : 'Start' }}
    </button> -->
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const API = 'http://localhost:8080'

const connected = ref(false)
const busy = ref(false)
const shooting = ref(false)
const statusText = ref('Checking camera...')
const liveUrl = ref('')
const lastPhoto = ref(null)

async function call(method, path) {
  const res = await fetch(API + path, { method })
  const body = await res.json()
  if (!res.ok) throw new Error(body.detail)
  return body
}

function applyStatus(s) {
  connected.value = s.connected
  statusText.value = s.connected ? 'Camera connected' : (s.error || 'Camera not connected')
  if (s.last_photo) lastPhoto.value = s.last_photo
  // A fresh URL makes the browser open a new stream after reconnecting.
  if (s.connected) liveUrl.value = `${API}/api/camera/live?t=${Date.now()}`
}

async function connect() {
  busy.value = true
  statusText.value = 'Connecting (takes a few seconds)...'
  try {
    applyStatus(await call('POST', '/api/camera/connect'))
  } catch (e) {
    statusText.value = e.message
  } finally {
    busy.value = false
  }
}

async function disconnect() {
  busy.value = true
  try {
    applyStatus(await call('POST', '/api/camera/disconnect'))
  } catch (e) {
    statusText.value = e.message
  } finally {
    busy.value = false
  }
}

async function shoot() {
  shooting.value = true
  try {
    lastPhoto.value = (await call('POST', '/api/camera/release')).photo
  } catch (e) {
    statusText.value = e.message
  } finally {
    shooting.value = false
  }
}

onMounted(async () => {
  try {
    applyStatus(await call('GET', '/api/camera/status'))
  } catch (e) {
    statusText.value = 'Could not reach backend'
  }
})
</script>

<style>
#vue-app {
  display: flex;
  flex-direction: column;
  align-items: center;
  row-gap: 1rem;
}

.live {
  width: 100%;
  max-width: 960px;
  background: #000;
}

.shutter {
  font-size: 1.5rem;
  padding: 1rem 3rem;
}

.photo {
  max-width: 320px;
}
</style>

<!-- <script setup>
import { watchEffect, ref, computed, onMounted } from 'vue';
import { useDevicesList, useUserMedia } from '@vueuse/core'

const {
  videoInputs: cameras,
} = useDevicesList({
  requestPermissions: true,
})

const videoRef = ref(null);

const currentCamera = computed(() => cameras.value[0]?.deviceId)

const { stream, enabled } = useUserMedia({
  constraints: {
    video: { deviceId: currentCamera },
  }
})

onMounted(() => {
  watchEffect(() => {
    if (videoRef.value && stream.value && stream.value.active) {
      videoRef.value.srcObject = stream.value;
    }
  })
})
</script>

<style>
#vue-app {
  display: flex;
  flex-direction: column;
  row-gap: 1rem;
}
</style> -->
