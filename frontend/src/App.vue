<template>
  <main class="booth">
    <!-- Live view stays mounted across start/countdown so the stream never restarts mid-shot. -->
    <img
      v-if="camera.connected"
      class="live"
      :class="{ mirrored: config.mirrorPreview }"
      :src="streamUrl"
      alt=""
    />

    <AttractScreen v-if="step === 'attract'" :ready="camera.connected" @start="start" />

    <CountdownOverlay
      v-else-if="step === 'countdown'"
      :seconds="config.countdownSeconds"
      @done="capture"
    />

    <ReviewScreen
      v-else-if="step === 'review'"
      :photo="photo"
      :idle-seconds="config.reviewIdleSeconds"
      @retake="start"
      @done="reset"
    />

    <div v-if="flash" class="flash" @animationend="flash = false"></div>
    <div v-if="step === 'capturing'" class="saving">Saving…</div>

    <div v-if="!camera.connected && camera.error" class="banner">
      {{ camera.error }} · retrying…
    </div>
    <div v-if="message" class="banner">{{ message }}</div>
  </main>
</template>

<script setup>
import { ref, reactive, onMounted, onBeforeUnmount } from 'vue'
import config from './config'
import { getStatus, takePhoto, liveUrl } from './api'
import AttractScreen from './components/AttractScreen.vue'
import CountdownOverlay from './components/CountdownOverlay.vue'
import ReviewScreen from './components/ReviewScreen.vue'

// attract -> countdown -> capturing -> review -> (retake: countdown | done: attract)
const step = ref('attract')
const photo = ref(null)
const flash = ref(false)
const message = ref('')
const camera = reactive({ connected: false, error: null })
const streamUrl = ref('')

function start() {
  if (!camera.connected) return
  step.value = 'countdown'
}

async function capture() {
  step.value = 'capturing'
  flash.value = true
  try {
    photo.value = await takePhoto()
    step.value = 'review'
  } catch (e) {
    showMessage(`Couldn't take the photo: ${e.message}`)
    reset()
  }
}

function reset() {
  step.value = 'attract'
  photo.value = null
}

let messageTimer
function showMessage(text) {
  message.value = text
  clearTimeout(messageTimer)
  messageTimer = setTimeout(() => (message.value = ''), 5000)
}

// The backend keeps the camera connected on its own; the UI just follows along.
async function refreshStatus() {
  try {
    const s = await getStatus()
    if (s.connected && !camera.connected) streamUrl.value = liveUrl()
    camera.connected = s.connected
    camera.error = s.error
  } catch {
    camera.connected = false
    camera.error = 'Booth is starting up'
  }
  if (!camera.connected && step.value === 'countdown') reset()
}

let pollTimer
onMounted(() => {
  refreshStatus()
  pollTimer = setInterval(refreshStatus, config.statusPollMs)
})
onBeforeUnmount(() => {
  clearInterval(pollTimer)
  clearTimeout(messageTimer)
})
</script>

<style scoped>
.booth {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
  background: #000;
}

.live {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.live.mirrored {
  transform: scaleX(-1);
}

.flash {
  position: absolute;
  inset: 0;
  background: #fff;
  pointer-events: none;
  animation: flash 0.6s ease-out forwards;
}

@keyframes flash {
  from { opacity: 1; }
  to { opacity: 0; }
}

.saving {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  font-weight: 600;
  background: rgba(0, 0, 0, 0.35);
}

.banner {
  position: absolute;
  top: 1.5rem;
  left: 50%;
  transform: translateX(-50%);
  max-width: calc(100% - 3rem);
  padding: 0.75rem 1.5rem;
  border-radius: 12px;
  background: var(--danger);
  font-size: 1.25rem;
  font-weight: 600;
  text-align: center;
}
</style>
