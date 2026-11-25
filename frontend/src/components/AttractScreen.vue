<template>
  <button class="attract" :disabled="!ready" @click="$emit('start')">
    <div class="panel">
      <h1 class="title">Snaptastic</h1>
      <p v-if="ready" class="cta">Tap anywhere to take a photo</p>
      <p v-else class="cta waiting">Getting the camera ready…</p>
    </div>
  </button>
</template>

<script setup>
defineProps({ ready: Boolean })
defineEmits(['start'])
</script>

<style scoped>
.attract {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  padding: 0 1.5rem 8vh;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.75), transparent 55%);
}

.panel {
  text-align: center;
}

.title {
  margin: 0;
  font-size: clamp(3rem, 9vw, 7rem);
  font-weight: 800;
  letter-spacing: -0.02em;
  background: linear-gradient(90deg, var(--accent), var(--accent-2));
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.cta {
  margin: 0.5rem 0 0;
  font-size: clamp(1.25rem, 3vw, 2.25rem);
  font-weight: 600;
  animation: pulse 2s ease-in-out infinite;
}

.cta.waiting {
  color: var(--muted);
  animation: none;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.45; }
}
</style>
