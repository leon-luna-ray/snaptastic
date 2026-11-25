<template>
  <div class="review" @pointerdown="resetIdle">
    <img class="photo" :src="photoUrl(photo)" alt="Your photo" />
    <div class="actions">
      <button class="btn secondary" @click="$emit('retake')">Retake</button>
      <button class="btn primary" @click="$emit('done')">Looks great!</button>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onBeforeUnmount } from 'vue'
import { photoUrl } from '../api'

const props = defineProps({
  photo: { type: String, required: true },
  idleSeconds: { type: Number, default: 30 },
})
const emit = defineEmits(['retake', 'done'])

// Nobody tapped for a while: whoever took the photo has walked away.
let idleTimer
function resetIdle() {
  clearTimeout(idleTimer)
  idleTimer = setTimeout(() => emit('done'), props.idleSeconds * 1000)
}

onMounted(resetIdle)
onBeforeUnmount(() => clearTimeout(idleTimer))
</script>

<style scoped>
.review {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4vh;
  padding: 4vh 1.5rem;
  background: var(--bg);
}

.photo {
  min-height: 0;
  max-width: 100%;
  flex: 1;
  object-fit: contain;
  border-radius: 12px;
  box-shadow: 0 1rem 3rem rgba(0, 0, 0, 0.6);
}

.actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 1.5rem;
}

.btn {
  min-width: 14rem;
  padding: 1.25rem 2.5rem;
  border-radius: 999px;
  font-size: clamp(1.25rem, 2.5vw, 2rem);
  font-weight: 700;
}

.btn:active {
  transform: scale(0.97);
}

.primary {
  background: linear-gradient(90deg, var(--accent), var(--accent-2));
  color: #111;
}

.secondary {
  background: rgba(255, 255, 255, 0.12);
  border: 2px solid rgba(255, 255, 255, 0.35);
}
</style>
