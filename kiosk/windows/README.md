# Running Snaptastic as a Windows kiosk

The booth is two pieces on one PC:

- **Backend** (Python, `http://localhost:8080`): drives the camera and serves the booth UI. A scheduled task starts it hidden when the kiosk account signs in.
- **Microsoft Edge in kiosk mode**: shows `http://localhost:8080` full screen. Windows **Assigned Access** locks the kiosk account so it can only run that.

Needs Windows 10/11 **Pro**, Enterprise or Education. Home has no Assigned Access.

## 1. Try it without locking anything

From an elevated PowerShell in the repo:

```powershell
# Builds the UI, installs to C:\Snaptastic and registers the task for *your* account
powershell -ExecutionPolicy Bypass -File kiosk\windows\setup.ps1 -InstallPrereqs
Start-ScheduledTask -TaskName 'Snaptastic Backend'

# Full-screen Edge pointed at the booth. Alt+F4 closes it.
powershell -ExecutionPolicy Bypass -File C:\Snaptastic\kiosk\launch-kiosk-dev.ps1
```

Check the backend: <http://localhost:8080/api/health>. Logs are in `C:\Snaptastic\backend\logs\backend.log`, and photos are saved to `C:\Snaptastic\backend\photos`.

Wrong webcam? Re-run setup with `-WebcamIndex 1` (or 2, …).

## 2. Create the kiosk account

1. **Settings → Accounts → Other users → Kiosk → Get started.**
2. Name the account, for example `Kiosk`.
3. Choose **Microsoft Edge** as the app.
4. Choose **As a digital sign or interactive display**.
5. URL: `http://localhost:8080`.
6. Set **Restart after a specified time of inactivity** to about **2 minutes**. This reloads the booth if Edge ever opens before the backend is ready, or if it loses the page.

Then point the backend task at that account (elevated PowerShell):

```powershell
powershell -ExecutionPolicy Bypass -File kiosk\windows\setup.ps1 -KioskUser Kiosk
```

## 3. Make the PC behave like an appliance

Do these as the admin account:

- **Camera privacy**: Settings → Privacy & security → Camera. Turn on **Camera access** and **Let desktop apps access your camera**.
- **Never sleep**: Settings → System → Power: screen and sleep → **Never**.
- **Updates**: Settings → Windows Update. Set **Active hours** to cover event times, or pause updates before an event.
- **Notifications**: the kiosk session hides most of them. Also turn off Settings → System → Notifications for the admin account.
- **Automatic sign-in**: a kiosk set up through Settings normally signs in by itself after a restart. If the PC stops at the sign-in screen instead, pick the kiosk account there once and check the kiosk settings again.

Reboot. The PC should land on the booth.

## Getting out of the kiosk

Press **Ctrl+Alt+Del**, then **Sign out** (or switch user), and sign in with the admin account. To remove the kiosk: Settings → Accounts → Other users → Kiosk → **Remove kiosk**.

## Updating

Pull the latest code, then run `kiosk\windows\setup.ps1 -KioskUser Kiosk` again. It rebuilds and recopies the code, but keeps photos, logs and the Python environment. Restart the kiosk account (sign out and back in) to load the new version.

## Switching to the Fujifilm camera

1. Copy `XAPI.dll` and the camera model DLLs from the Fujifilm SDK into `backend\camera\dll\` in the repo. They are git-ignored, so they stay local.
2. Set the camera to **USB TETHER SHOOTING AUTO**.
3. Run `kiosk\windows\setup.ps1 -KioskUser Kiosk -Camera fuji`.

## Troubleshooting

| Symptom | Check |
|---|---|
| "Hmm, can't reach this page" | The backend isn't running. Look at `logs\backend.log`, and check Task Scheduler → *Snaptastic Backend* → History. |
| Banner: "No webcam found at index 0" | Another app holds the camera, the privacy settings above are off, or the wrong `-WebcamIndex` is set. |
| Black live view | Some webcams don't do 1080p MJPEG. Try another USB port, or check the log. |
| Need the mouse while testing | Add `?cursor` to the URL: `http://localhost:8080/?cursor`. |
