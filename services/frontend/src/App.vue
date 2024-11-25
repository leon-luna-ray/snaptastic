<template>
  <div id="vue-app">
    <h1 class="icons">Snaptastic</h1>
    <video id="video" ref="videoRef" muted autoplay></video>
    <button @click="enabled = !enabled">
      {{ enabled ? 'Stop' : 'Start' }}
    </button>
  </div>
</template>

<script setup>
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
</style>
