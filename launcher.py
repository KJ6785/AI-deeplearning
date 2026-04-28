import os
import sys
import subprocess
import time
from src.ui.app_gui import GRAVWindow
from PyQt6.QtWidgets import QApplication

# ASCII 로딩 화면
GRAV_SPLASH = """
    ╔═══════════════════════════════════════════════════════╗
    ║                                                       ║
    ║        ░██████╗░██████╗░░█████╗░██╗░░░██╗            ║
    ║        ██╔════╝░██╔══██╗██╔══██╗██║░░░██║            ║
    ║        ██║░░██╗░██████╔╝███████║╚██╗░██╔╝            ║
    ║        ██║░░╚██╗██╔══██╗██╔══██║░╚████╔╝░            ║
    ║        ╚██████╔╝██║░░██║██║░░██║░░╚██╔╝░░            ║
    ║        ░╚═════╝░╚═╝░░╚═╝╚═╝░░╚═╝░░░╚═╝░░░            ║
    ║                                                       ║
    ║           Galaxy Rotation Analyze Viewer       ║
    ║                                                       ║
    ║                  ∴ · ∘ ◦ ● ◦ ∘ · ∴                   ║
    ║              ∘ ◦ ● ◉ ▣ GRAV ▣ ◉ ● ◦ ∘                ║
    ║                  ∴ · ∘ ◦ ● ◦ ∘ · ∴                   ║
    ║                                                       ║
    ║              Initializing Desktop UI...              ║
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝
"""

def main():
    # 1. 터미널에 로딩 화면 출력
    os.system('cls' if os.name == 'nt' else 'clear')
    print(GRAV_SPLASH)
    
    print("\n   [✓] System Initialized.")
    print("   [✓] Starting GRAV Desktop Application...")
    
    # 2. PyQt6 GUI 실행
    app = QApplication(sys.argv)
    window = GRAVWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
