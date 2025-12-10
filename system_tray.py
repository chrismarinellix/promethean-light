"""System Tray Application for Promethean Light - One-Click Start"""

import sys
import os
import subprocess
import threading
import socket
import ctypes
import tkinter as tk
from tkinter import simpledialog
from pathlib import Path
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item

# Default API port
API_PORT = 8000
API_HOST = "127.0.0.1"

# Paths
SCRIPT_DIR = Path(__file__).parent
UI_EXE = SCRIPT_DIR / "promethean-light-ui" / "src-tauri" / "target" / "release" / "promethean-light-ui.exe"


def is_daemon_running():
    """Check if the daemon is already running by testing the API port"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((API_HOST, API_PORT))
        sock.close()
        return result == 0
    except:
        return False


def get_passphrase():
    """Show a dialog to get the passphrase"""
    root = tk.Tk()
    root.withdraw()  # Hide main window
    root.attributes('-topmost', True)  # Keep on top

    passphrase = simpledialog.askstring(
        "Promethean Light",
        "Enter your passphrase:",
        show='*',
        parent=root
    )
    root.destroy()
    return passphrase


class PrometheanTray:
    """System tray application for Promethean Light"""

    def __init__(self):
        self.daemon_process = None
        self.icon = None
        self.is_running = is_daemon_running()
        print(f"[TRAY] Init: daemon already running = {self.is_running}")

    def create_icon_image(self, running=False):
        """Create a Prometheus-themed icon (fire/torch)"""
        size = 64
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        if running:
            # Bright fire colors when running
            flame_colors = [(255, 69, 0), (255, 140, 0), (255, 215, 0)]
            handle_color = (101, 67, 33)
            bowl_color = (139, 90, 43)
        else:
            # Dimmed colors when stopped
            flame_colors = [(128, 35, 0), (128, 70, 0), (128, 107, 0)]
            handle_color = (60, 40, 20)
            bowl_color = (80, 50, 25)

        # Base/handle
        draw.rectangle([(28, 45), (36, 60)], fill=handle_color)

        # Torch bowl
        draw.ellipse([(20, 35), (44, 50)], fill=bowl_color)

        # Flames
        flame_outer = [(32, 10), (20, 30), (32, 40), (44, 30)]
        draw.polygon(flame_outer, fill=flame_colors[0])

        flame_mid = [(32, 15), (24, 30), (32, 38), (40, 30)]
        draw.polygon(flame_mid, fill=flame_colors[1])

        flame_inner = [(32, 18), (28, 30), (32, 35), (36, 30)]
        draw.polygon(flame_inner, fill=flame_colors[2])

        return img

    def update_icon(self):
        """Update the icon based on running state"""
        if self.icon:
            self.icon.icon = self.create_icon_image(self.is_running)

    def start_daemon(self, icon_obj=None):
        """Start the Promethean Light daemon and UI"""
        print(f"[TRAY] start_daemon called")

        if self.is_running:
            print("[TRAY] Already running, just launch UI")
            self.launch_ui()
            return

        # Check if daemon is already running externally
        if is_daemon_running():
            print("[TRAY] Daemon detected on port, connecting...")
            self.is_running = True
            self.update_icon()
            self.show_notification("Connected to existing daemon")
            self.launch_ui()
            if icon_obj:
                icon_obj.update_menu()
            return

        # Get passphrase
        passphrase = get_passphrase()
        if not passphrase:
            self.show_notification("Cancelled - no passphrase entered")
            return

        def run():
            try:
                # Set environment and start daemon
                env = os.environ.copy()
                env['MYDATA_PASSPHRASE'] = passphrase
                env['API_HOST'] = '0.0.0.0'
                env['API_PORT'] = str(API_PORT)

                # Start daemon (hidden console)
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = 0  # SW_HIDE

                self.daemon_process = subprocess.Popen(
                    [sys.executable, "-u", "-m", "mydata", "daemon"],
                    cwd=str(SCRIPT_DIR),
                    env=env,
                    startupinfo=startupinfo,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )

                # Wait for daemon to be ready (up to 60 seconds)
                import time
                for i in range(60):
                    time.sleep(1)
                    if is_daemon_running():
                        break
                    if self.daemon_process.poll() is not None:
                        # Process died
                        self.show_notification("Daemon failed to start")
                        return

                if is_daemon_running():
                    self.is_running = True
                    self.update_icon()
                    self.show_notification("Promethean Light started!")
                    self.launch_ui()
                    if icon_obj:
                        icon_obj.update_menu()
                else:
                    self.show_notification("Daemon startup timed out")

            except Exception as e:
                self.show_notification(f"Failed to start: {e}")
                print(f"[TRAY] Error: {e}")

        thread = threading.Thread(target=run, daemon=True)
        thread.start()

    def launch_ui(self):
        """Launch the Tauri UI"""
        if UI_EXE.exists():
            try:
                subprocess.Popen([str(UI_EXE)], cwd=str(SCRIPT_DIR))
                print(f"[TRAY] Launched UI: {UI_EXE}")
            except Exception as e:
                print(f"[TRAY] Failed to launch UI: {e}")
                # Fallback to web browser
                import webbrowser
                webbrowser.open(f"http://{API_HOST}:{API_PORT}/dashboard")
        else:
            # Fallback to web browser
            import webbrowser
            webbrowser.open(f"http://{API_HOST}:{API_PORT}/dashboard")

    def stop_daemon(self, icon_obj=None):
        """Stop the daemon"""
        if not self.is_running:
            return

        if self.daemon_process:
            try:
                self.daemon_process.terminate()
                self.daemon_process.wait(timeout=5)
            except:
                pass
            self.daemon_process = None

        # Also kill any process on the port
        try:
            import subprocess
            result = subprocess.run(
                ['netstat', '-ano'],
                capture_output=True,
                text=True
            )
            for line in result.stdout.split('\n'):
                if f':{API_PORT}' in line and 'LISTENING' in line:
                    parts = line.split()
                    if parts:
                        pid = parts[-1]
                        subprocess.run(['taskkill', '/F', '/PID', pid],
                                      capture_output=True)
        except:
            pass

        self.is_running = False
        self.update_icon()
        self.show_notification("Promethean Light stopped")
        if icon_obj:
            icon_obj.update_menu()

    def open_ui(self, icon_obj=None):
        """Open the UI"""
        if self.is_running:
            self.launch_ui()
        else:
            self.show_notification("Start the daemon first")

    def open_web(self, icon_obj=None):
        """Open web dashboard"""
        import webbrowser
        webbrowser.open(f"http://{API_HOST}:{API_PORT}/dashboard")

    def show_notification(self, message):
        """Show notification"""
        if self.icon:
            try:
                self.icon.notify(message, "Promethean Light")
            except:
                print(f"[TRAY] Notification: {message}")

    def quit_app(self, icon_obj):
        """Quit the application"""
        self.stop_daemon()
        icon_obj.stop()

    def create_menu(self):
        """Create the system tray menu"""
        return pystray.Menu(
            item(
                'Start Promethean Light',
                self.start_daemon,
                default=True,  # Double-click action
                visible=lambda item: not self.is_running
            ),
            item(
                'Open UI',
                self.open_ui,
                default=True,  # Double-click action when running
                visible=lambda item: self.is_running
            ),
            item(
                'Stop Daemon',
                self.stop_daemon,
                visible=lambda item: self.is_running
            ),
            pystray.Menu.SEPARATOR,
            item('Web Dashboard', self.open_web),
            pystray.Menu.SEPARATOR,
            item('Quit', self.quit_app)
        )

    def run(self):
        """Run the system tray application"""
        # Create icon
        icon_image = self.create_icon_image(self.is_running)

        self.icon = pystray.Icon(
            "promethean_light",
            icon_image,
            "Promethean Light",
            menu=self.create_menu()
        )

        # Show startup notification
        status = "Running" if self.is_running else "Ready"
        self.icon.notify(f"Promethean Light - {status}", "Promethean Light")

        # Run the icon
        self.icon.run()


def main():
    """Main entry point"""
    try:
        app = PrometheanTray()
        app.run()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
