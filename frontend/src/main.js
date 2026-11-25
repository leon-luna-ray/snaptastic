import { createApp } from 'vue'
import './style.css'
import App from './App.vue'

// Kiosk hardening: no right-click / long-press menu, no pinch or ctrl+wheel zoom.
window.addEventListener('contextmenu', (e) => e.preventDefault())
window.addEventListener('wheel', (e) => { if (e.ctrlKey) e.preventDefault() }, { passive: false })
window.addEventListener('gesturestart', (e) => e.preventDefault())
window.addEventListener('dragstart', (e) => e.preventDefault())

if (new URLSearchParams(location.search).has('cursor')) {
  document.body.classList.add('show-cursor')
}

createApp(App).mount('#app')
