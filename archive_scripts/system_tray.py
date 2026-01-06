"""System Tray Application for Promethean Light"""

import sys
import os
import subprocess
import threading
import socket
from pathlib import Path
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item
import webbrowser

# Default API port - should match mydata/settings.py
API_PORT = 8000
API_HOST = "127.0.0.1"


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


class PrometheanTray:
    """System tray application for Promethean Light"""

    def __init__(self):
        self.daemon_process = None
        self.icon = None
        # Check if daemon is already running on init
        self.is_running = is_daemon_running()
        print(f"[TRAY] Init: daemon already running = {self.is_running}")

    def create_icon_image(self):
        """Create a Prometheus-themed icon (fire/torch)"""
        # Create 64x64 icon with transparency
        size = 64
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Gradient fire colors (orange to yellow)
        colors = [
            (255, 69, 0),    # Red-Orange
            (255, 140, 0),   # Dark Orange
            (255, 165, 0),   # Orange
            (255, 215, 0),   # Gold
            (255, 255, 0),   # Yellow
        ]

        # Draw flame shape (stylized torch)
        # Base/handle
        draw.rectangle([(28, 45), (36, 60)], fill=(101, 67, 33))  # Brown handle

        # Torch bowl
        draw.ellipse([(20, 35), (44, 50)], fill=(139, 90, 43))  # Bronze bowl

        # Flames (layered tear-drop shapes)
        # Outer flame (red-orange)
        flame_outer = [
            (32, 10),   # Top point
            (20, 30),   # Left curve
            (32, 40),   # Bottom center
            (44, 30),   # Right curve
        ]
        draw.polygon(flame_outer, fill=colors[0])

        # Middle flame (orange)
        flame_mid = [
            (32, 15),
            (24, 30),
            (32, 38),
            (40, 30),
        ]
        draw.polygon(flame_mid, fill=colors[2])

        # Inner flame (yellow)
        flame_inner = [
            (32, 18),
            (28, 30),
            (32, 35),
            (36, 30),
        ]
        draw.polygon(flame_inner, fill=colors[4])

        # Add glow effect
        for i in range(3):
            alpha = 30 - (i * 10)
            glow_size = 50 - (i * 3)
            offset = (size - glow_size) // 2
            draw.ellipse(
                [(offset, offset - 10), (offset + glow_size, offset + glow_size - 10)],
                fill=(255, 200, 0, alpha)
            )

        return img

    def create_icon_file(self):
        """Create .ico file from image"""
        icon_path = Path(__file__).parent / "promethean.ico"
        img = self.create_icon_image()

        # Save as multi-resolution .ico
        img.save(icon_path, format='ICO', sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
        return icon_path

    def start_daemon(self, icon_obj=None):
        """Start the Promethean Light daemon"""
        print(f"[TRAY] start_daemon called, is_running = {self.is_running}")
        if self.is_running:
            print("[TRAY] Already running, returning early")
            return

        # Check if daemon is already running externally
        if is_daemon_running():
            print("[TRAY] Daemon detected on port, connecting...")
            self.is_running = True
            self.daemon_process = None  # We didn't start it, so no process to track
            self.show_notification("Connected to existing daemon")
            if icon_obj:
                icon_obj.update_menu()
            return

        def run():
            try:
                # Get the directory where this script is located
                script_dir = Path(__file__).parent

                # Start daemon in new console window
                self.daemon_process = subprocess.Popen(
                    [sys.executable, "-m", "mydata", "daemon"],
                    cwd=str(script_dir),
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
                self.is_running = True

                # Update menu
                if icon_obj:
                    icon_obj.update_menu()

            except Exception as e:
                self.show_notification(f"Failed to start: {e}")

        thread = threading.Thread(target=run, daemon=True)
        thread.start()

    def stop_daemon(self, icon_obj=None):
        """Stop the daemon"""
        if not self.is_running:
            return

        # If we started the daemon, terminate it
        if self.daemon_process:
            try:
                self.daemon_process.terminate()
                self.daemon_process.wait(timeout=5)
                self.is_running = False
                self.daemon_process = None

                # Update menu
                if icon_obj:
                    icon_obj.update_menu()

            except Exception as e:
                self.show_notification(f"Failed to stop: {e}")
        else:
            # Daemon was already running externally - just disconnect
            self.is_running = False
            self.show_notification("Disconnected from daemon")
            if icon_obj:
                icon_obj.update_menu()

    def open_web_interface(self, icon_obj=None):
        """Open the web interface in browser"""
        webbrowser.open("http://localhost:8000")

    def open_quick_menu(self, icon_obj=None):
        """Open quick access menu"""
        script_dir = Path(__file__).parent
        subprocess.Popen(
            [sys.executable, "-m", "mydata", "quick"],
            cwd=str(script_dir),
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )

    def show_notification(self, message):
        """Show notification (if icon exists)"""
        if self.icon:
            self.icon.notify(message, "Promethean Light")

    def quit_app(self, icon_obj):
        """Quit the application"""
        self.stop_daemon()
        icon_obj.stop()

    def create_menu(self):
        """Create the system tray menu"""
        return pystray.Menu(
            item(
                'Start God Mode',
                self.start_daemon,
                visible=lambda item: not self.is_running
            ),
            item(
                'Stop God Mode',
                self.stop_daemon,
                visible=lambda item: self.is_running
            ),
            item(
                '─────────────',
                None,
                enabled=False
            ),
            item('Quick Access Menu', self.open_quick_menu),
            item('Web Interface', self.open_web_interface),
            item(
                '─────────────',
                None,
                enabled=False
            ),
            item('Quit', self.quit_app)
        )

    def run(self):
        """Run the system tray application"""
        # Create icon file
        icon_path = self.create_icon_file()

        # Create icon image
        icon_image = Image.open(icon_path)

        # Create system tray icon
        self.icon = pystray.Icon(
            "promethean_light",
            icon_image,
            "Promethean Light - God Mode",
            menu=self.create_menu()
        )

        # Show startup notification
        if self.is_running:
            self.icon.notify("Connected to running daemon", "Promethean Light")
        else:
            self.icon.notify("System Tray Loaded", "Promethean Light")

        # Run the icon (blocks until quit)
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
