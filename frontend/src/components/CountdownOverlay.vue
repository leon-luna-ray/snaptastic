<template>
  <div class="countdown">
    <!-- :key restarts the pop animation for each number -->
    <span :key="remaining" class="number">{{ remaining }}</span>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

const props = defineProps({ seconds: { type: Number, default: 3 } })
const emit = defineEmits(['done'])

const remaining = ref(props.seconds)
let timer

onMounted(() => {
  timer = setInterval(() => {
    if (remaining.value <= 1) {
      clearInterval(timer)
      emit('done')
    } else {
      remaining.value--
    }
  }, 1000)
})

onBeforeUnmount(() => clearInterval(timer))
</script>

<style scoped>
.countdown {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}

.number {
  font-size: min(45vh, 45vw);
  font-weight: 800;
  line-height: 1;
  color: #fff;
  text-shadow: 0 0.04em 0.2em rgba(0, 0, 0, 0.6);
  animation: pop 1s ease-out;
}

@keyframes pop {
  0% { transform: scale(1.6); opacity: 0; }
  20% { transform: scale(1); opacity: 1; }
  85% { opacity: 1; }
  100% { transform: scale(0.85); opacity: 0; }
}
</style>
