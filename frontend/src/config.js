// Booth settings. Change these and rebuild (`pnpm build`).
export default {
  countdownSeconds: 3,
  // Review screen goes back to the start screen after this long without a tap.
  reviewIdleSeconds: 30,
  // Show the live view like a mirror. The saved photo is never mirrored.
  mirrorPreview: true,
  // How often to check the camera status.
  statusPollMs: 2000,
}
