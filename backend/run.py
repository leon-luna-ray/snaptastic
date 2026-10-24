"""Start the backend: `venv/bin/python run.py` from the backend folder.

On macOS the Fujifilm SDK talks to the camera through Apple's USB camera
framework, which delivers its events on the main thread's run loop. Without a
running main run loop, camera detection never sees the camera and XSDK_Exit
hangs forever. So on macOS uvicorn runs in a background thread and the main
thread keeps that run loop going.
"""
import platform
import signal
import threading
from ctypes import CDLL, c_bool, c_double, c_void_p

import uvicorn

# timeout_graceful_shutdown: an open live view stream never finishes on its own,
# so don't wait for it forever when stopping the server.
server = uvicorn.Server(
    uvicorn.Config("src.main:app", host="127.0.0.1", port=8080, timeout_graceful_shutdown=2)
)


def main():
    if platform.system() != "Darwin":
        server.run()
        return

    cf = CDLL("/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation")
    cf.CFRunLoopRunInMode.argtypes = [c_void_p, c_double, c_bool]
    default_mode = c_void_p.in_dll(cf, "kCFRunLoopDefaultMode")

    # uvicorn only handles signals on the main thread, so turn Ctrl+C and
    # `kill` into a KeyboardInterrupt here and stop the server ourselves.
    signal.signal(signal.SIGINT, signal.default_int_handler)
    signal.signal(signal.SIGTERM, signal.default_int_handler)

    thread = threading.Thread(target=server.run)
    thread.start()
    while True:
        try:
            if not thread.is_alive():
                break
            # Returns every 0.1s so Ctrl+C gets a chance to be handled.
            cf.CFRunLoopRunInMode(default_mode, 0.1, False)
        except KeyboardInterrupt:
            # Keep pumping the run loop while the server shuts down, since
            # disconnecting the camera needs it. A second Ctrl+C forces exit.
            if server.should_exit:
                server.force_exit = True
            server.should_exit = True


if __name__ == "__main__":
    main()
