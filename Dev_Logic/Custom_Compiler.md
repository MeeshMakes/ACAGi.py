# Project Documentation

## Table of Contents
- [Overview](#overview)
- [Python Modules](#python-modules)
- [Other Files](#other-files)

## Overview
This README was generated automatically by analysing the contents of the project.  The analysis focuses primarily on Python modules, extracting module documentation, classes and functions.  Other file types are listed for completeness.

## Python Modules

### `Analyze_folders.py`

**Functions:** analyze_folders(start_path)
### `ico_converter.py`

**Classes:** Worker, MainWindow

**Functions:** main()
### `OLD_game_packager.py`

Enhanced Panda3D packager / auditor / Steam uploader GUI.

New Features:
• Project folder selection with dropdown menu from C:\\Users\\Art PC\\Desktop\\Custom_Compiler\\Projects
• Original game folder input with cloning to prevent tampering
• Enhanced tooltips for all settings with 3-second delay
• Prompt management system with Ollama integration
• Default prompt templates auto-creation
• Improved project structure display
• Enhanced Steam configuration with username and validation
• Integration with Steamworks SDK in sdk/ folder
• Full project snapshot generation with AI-powered analysis
• ISO generation
• oscdimg/mkisofs support
• Icon converter launcher
• UPX-path override

**Classes:** SlowTipStyle, Worker, MainWindow

**Functions:** create_default_prompts(prompts_dir), audit_project(project_dir), generate_project_snapshot(root_path, include_hidden), exception_handler(type, value, tb)
### `panel_creator.py`

tests/panel_creator.py

A quick PyQt5‑based Panel/Scene Generator for Rats n Goblins (now in tests/):
• Enter a panel/scene name (CamelCase)
• Select target folder or script via a scrollable tree view of the entire project
• Choose to generate a Python panel script (launches it briefly to auto‑generate SB)
  or an SB template for an existing script
• “Generate” writes the file(s) and logs their paths + contents in the Output Log
• “Delete” removes the selected file (with confirmation)
• “Ctrl+Z” undoes the last deletion
• “Copy Log” copies the entire Output Log to clipboard
• “Refresh” clears inputs and the Output Log for the next session

**Classes:** PanelCreator

**Functions:** main()
### `Simple_Packager.py`

This script provides a GUI front‑end for packaging Panda3D games into
self‑contained executables.  It clones a project into a temporary
directory, invokes PyInstaller to build a one‑file binary and then
optionally retries with user‑supplied fixes if the build fails.  The
script has been enhanced to better handle Panda3D projects: it will
automatically discover a project‑local virtual environment, include
data directories (e.g. models or textures) via PyInstaller's
``--add-data`` option and collect all resources from the ``panda3d``
package.

**Classes:** SlowTipStyle, BuildWindow, Worker, MainWindow

**Functions:** qt_message_handler(msg_type, ctx, msg), clean_clone(src, dst, log_fn), exception_handler(t, v, tb)
### `Projects\TestGame3D\clone\main.py`

**Classes:** Item, Character, EnhancedRPG

**Functions:** main()
### `sdk\tools\codesigning\build_steam_signatures_file.py`

**Functions:** printw(message), usage(), readkeyfile(publickeyfilename), signmessage_add_digest(message, privatekeyfile), checkdigest(signaturefilename, key), crchex(crc32), parsehashes(message, pathto), signatures_need_update(signaturefilename, publickeyfilename), write_new_signature_file(signaturefilename, publickeyfilename, privatekeyfilename, newsignaturefilename), main()

## Other Files

The following files are present in the project but were not analysed in detail:

- `Builds\TestGame3D\TestGame3D.exe`
- `Ico Inbound\RatsNGoblinsISO.png`
- `Ico Outbound\MyGameIcon.ico`
- `Panda3D_packaging_practices.txt`
- `Projects\TestGame3D\.game_tool_config.json`
- `activity.log`
- `analyze.txt`
- `bat.bat`
- `build.log`
- `ico_converter_config.json`
- `prompts\build_optimization.txt`
- `prompts\code_analysis.txt`
- `prompts\deployment_checklist.txt`
- `prompts\diagnose.txt`
- `prompts\package.txt`
- `prompts\security_audit.txt`
- `sdk\Readme.txt`
- `sdk\glmgr\cglmbuffer.cpp`
- `sdk\glmgr\cglmbuffer.h`
- `sdk\glmgr\cglmfbo.cpp`
- `sdk\glmgr\cglmfbo.h`
- `sdk\glmgr\cglmprogram.cpp`
- `sdk\glmgr\cglmprogram.h`
- `sdk\glmgr\cglmquery.cpp`
- `sdk\glmgr\cglmquery.h`
- `sdk\glmgr\cglmtex.cpp`
- `sdk\glmgr\cglmtex.h`
- `sdk\glmgr\dx9asmtogl2.cpp`
- `sdk\glmgr\dx9asmtogl2.h`
- `sdk\glmgr\dxabstract.cpp`
- `sdk\glmgr\dxabstract.h`
- `sdk\glmgr\glmdebug.h`
- `sdk\glmgr\glmdisplay.h`
- `sdk\glmgr\glmgr.cpp`
- `sdk\glmgr\glmgr.h`
- `sdk\glmgr\glmgrbasics.cpp`
- `sdk\glmgr\glmgrbasics.h`
- `sdk\glmgr\glmgrcocoa.mm`
- `sdk\glmgr\glmgrext.cpp`
- `sdk\glmgr\glmgrext.h`
- `sdk\glmgr\imageformat.h`
- `sdk\glmgr\mathlite.cpp`
- `sdk\glmgr\mathlite.h`
- `sdk\glmgr\readme.txt`
- `sdk\public\steam\isteamapps.h`
- `sdk\public\steam\isteamappticket.h`
- `sdk\public\steam\isteamclient.h`
- `sdk\public\steam\isteamcontroller.h`
- `sdk\public\steam\isteamdualsense.h`
- `sdk\public\steam\isteamfriends.h`
- `sdk\public\steam\isteamgamecoordinator.h`
- `sdk\public\steam\isteamgameserver.h`
- `sdk\public\steam\isteamgameserverstats.h`
- `sdk\public\steam\isteamhtmlsurface.h`
- `sdk\public\steam\isteamhttp.h`
- `sdk\public\steam\isteaminput.h`
- `sdk\public\steam\isteaminventory.h`
- `sdk\public\steam\isteammatchmaking.h`
- `sdk\public\steam\isteammusic.h`
- `sdk\public\steam\isteammusicremote.h`
- `sdk\public\steam\isteamnetworking.h`
- `sdk\public\steam\isteamnetworkingmessages.h`
- `sdk\public\steam\isteamnetworkingsockets.h`
- `sdk\public\steam\isteamnetworkingutils.h`
- `sdk\public\steam\isteamparentalsettings.h`
- `sdk\public\steam\isteamps3overlayrenderer.h`
- `sdk\public\steam\isteamremoteplay.h`
- `sdk\public\steam\isteamremotestorage.h`
- `sdk\public\steam\isteamscreenshots.h`
- `sdk\public\steam\isteamtimeline.h`
- `sdk\public\steam\isteamugc.h`
- `sdk\public\steam\isteamuser.h`
- `sdk\public\steam\isteamuserstats.h`
- `sdk\public\steam\isteamutils.h`
- `sdk\public\steam\isteamvideo.h`
- `sdk\public\steam\lib\linux32\libsdkencryptedappticket.so`
- `sdk\public\steam\lib\linux64\libsdkencryptedappticket.so`
- `sdk\public\steam\lib\osx\libsdkencryptedappticket.dylib`
- `sdk\public\steam\lib\win32\sdkencryptedappticket.dll`
- `sdk\public\steam\lib\win32\sdkencryptedappticket.lib`
- `sdk\public\steam\lib\win64\sdkencryptedappticket64.dll`
- `sdk\public\steam\lib\win64\sdkencryptedappticket64.lib`
- `sdk\public\steam\matchmakingtypes.h`
- `sdk\public\steam\steam_api.h`
- `sdk\public\steam\steam_api.json`
- `sdk\public\steam\steam_api_common.h`
- `sdk\public\steam\steam_api_flat.h`
- `sdk\public\steam\steam_api_internal.h`
- `sdk\public\steam\steam_gameserver.h`
- `sdk\public\steam\steamclientpublic.h`
- `sdk\public\steam\steamencryptedappticket.h`
- `sdk\public\steam\steamhttpenums.h`
- `sdk\public\steam\steamnetworkingfakeip.h`
- `sdk\public\steam\steamnetworkingtypes.h`
- `sdk\public\steam\steamps3params.h`
- `sdk\public\steam\steamtypes.h`
- `sdk\public\steam\steamuniverse.h`
- `sdk\redistributable_bin\linux32\libsteam_api.so`
- `sdk\redistributable_bin\linux64\libsteam_api.so`
- `sdk\redistributable_bin\osx\libsteam_api.dylib`
- `sdk\redistributable_bin\steam_api.dll`
- `sdk\redistributable_bin\steam_api.lib`
- `sdk\redistributable_bin\win64\steam_api64.dll`
- `sdk\redistributable_bin\win64\steam_api64.lib`
- `sdk\steamworksexample\BaseMenu.cpp`
- `sdk\steamworksexample\BaseMenu.h`
- `sdk\steamworksexample\D3D9VRDistort.cso`
- `sdk\steamworksexample\DejaVuSans.ttf`
- `sdk\steamworksexample\DejaVuSans.txt`
- `sdk\steamworksexample\Friends.cpp`
- `sdk\steamworksexample\Friends.h`
- `sdk\steamworksexample\GL\glew.h`
- `sdk\steamworksexample\GL\glxew.h`
- `sdk\steamworksexample\GL\wglew.h`
- `sdk\steamworksexample\GameEngine.h`
- `sdk\steamworksexample\Inventory.cpp`
- `sdk\steamworksexample\Inventory.h`
- `sdk\steamworksexample\ItemStore.cpp`
- `sdk\steamworksexample\ItemStore.h`
- `sdk\steamworksexample\Leaderboards.cpp`
- `sdk\steamworksexample\Leaderboards.h`
- `sdk\steamworksexample\Lobby.cpp`
- `sdk\steamworksexample\Lobby.h`
- `sdk\steamworksexample\Main.cpp`
- `sdk\steamworksexample\MainMenu.cpp`
- `sdk\steamworksexample\MainMenu.h`
- `sdk\steamworksexample\Makefile`
- `sdk\steamworksexample\Messages.h`
- `sdk\steamworksexample\NEU\SpaceWar.gdf.xml`
- `sdk\steamworksexample\NEU\boxart_NEU.png`
- `sdk\steamworksexample\NEU\gameicon_NEU.ico`
- `sdk\steamworksexample\OverlayExamples.cpp`
- `sdk\steamworksexample\OverlayExamples.h`
- `sdk\steamworksexample\PhotonBeam.cpp`
- `sdk\steamworksexample\PhotonBeam.h`
- `sdk\steamworksexample\QuitMenu.cpp`
- `sdk\steamworksexample\QuitMenu.h`
- `sdk\steamworksexample\RemotePlay.cpp`
- `sdk\steamworksexample\RemotePlay.h`
- `sdk\steamworksexample\RemoteStorage.cpp`
- `sdk\steamworksexample\RemoteStorage.h`
- `sdk\steamworksexample\ServerBrowser.cpp`
- `sdk\steamworksexample\ServerBrowser.h`
- `sdk\steamworksexample\ServerBrowserMenu.h`
- `sdk\steamworksexample\Ship.cpp`
- `sdk\steamworksexample\Ship.h`
- `sdk\steamworksexample\SimpleProtobuf.cpp`
- `sdk\steamworksexample\SimpleProtobuf.h`
- `sdk\steamworksexample\SpaceWar.h`
- `sdk\steamworksexample\SpaceWarClient.cpp`
- `sdk\steamworksexample\SpaceWarClient.h`
- `sdk\steamworksexample\SpaceWarEntity.cpp`
- `sdk\steamworksexample\SpaceWarEntity.h`
- `sdk\steamworksexample\SpaceWarRes.h`
- `sdk\steamworksexample\SpaceWarRes.rc`
- `sdk\steamworksexample\SpaceWarServer.cpp`
- `sdk\steamworksexample\SpaceWarServer.h`
- `sdk\steamworksexample\StarField.cpp`
- `sdk\steamworksexample\StarField.h`
- `sdk\steamworksexample\StatsAndAchievements.cpp`
- `sdk\steamworksexample\StatsAndAchievements.h`
- `sdk\steamworksexample\SteamWorksExample.exe.manifest`
- `sdk\steamworksexample\SteamworksExample.sh`
- `sdk\steamworksexample\SteamworksExample.sln`
- `sdk\steamworksexample\SteamworksExample.vcxproj`
- `sdk\steamworksexample\SteamworksExample.vcxproj.filters`
- `sdk\steamworksexample\Sun.cpp`
- `sdk\steamworksexample\Sun.h`
- `sdk\steamworksexample\VectorEntity.cpp`
- `sdk\steamworksexample\VectorEntity.h`
- `sdk\steamworksexample\clanchatroom.cpp`
- `sdk\steamworksexample\clanchatroom.h`
- `sdk\steamworksexample\debug\steam_appid.txt`
- `sdk\steamworksexample\flags.mak`
- `sdk\steamworksexample\gameengineosx.h`
- `sdk\steamworksexample\gameengineosx.mm`
- `sdk\steamworksexample\gameengineps3.cpp`
- `sdk\steamworksexample\gameengineps3.h`
- `sdk\steamworksexample\gameenginesdl.cpp`
- `sdk\steamworksexample\gameenginesdl.h`
- `sdk\steamworksexample\gameenginewin32.cpp`
- `sdk\steamworksexample\gameenginewin32.h`
- `sdk\steamworksexample\glew.c`
- `sdk\steamworksexample\glstringosx.h`
- `sdk\steamworksexample\glstringosx.mm`
- `sdk\steamworksexample\htmlsurface.cpp`
- `sdk\steamworksexample\htmlsurface.h`
- `sdk\steamworksexample\musicplayer.cpp`
- `sdk\steamworksexample\musicplayer.h`
- `sdk\steamworksexample\osx\steam_appid.txt`
- `sdk\steamworksexample\osx\steamworksexample-info.plist`
- `sdk\steamworksexample\osx\steamworksexample.entitlements`
- `sdk\steamworksexample\p2pauth.cpp`
- `sdk\steamworksexample\p2pauth.h`
- `sdk\steamworksexample\release\steam_appid.txt`
- `sdk\steamworksexample\richpresenceloc.vdf`
- `sdk\steamworksexample\stdafx.cpp`
- `sdk\steamworksexample\stdafx.h`
- `sdk\steamworksexample\stdafx_ps3.h`
- `sdk\steamworksexample\steam_controller.vdf`
- `sdk\steamworksexample\steam_input_manifest.vdf`
- `sdk\steamworksexample\steamworksexample.xcodeproj\project.pbxproj`
- `sdk\steamworksexample\timeline.cpp`
- `sdk\steamworksexample\timeline.h`
- `sdk\steamworksexample\voicechat.cpp`
- `sdk\steamworksexample\voicechat.h`
- `sdk\steamworksexample\win64\debug\steam_appid.txt`
- `sdk\steamworksexample\win64\release\steam_appid.txt`
- `sdk\steamworksexample\xbox_controller.vdf`
- `sdk\tools\ContentBuilder\builder\steamcmd.exe`
- `sdk\tools\ContentBuilder\builder_linux\linux32\crashhandler.so`
- `sdk\tools\ContentBuilder\builder_linux\linux32\libstdc++.so.6`
- `sdk\tools\ContentBuilder\builder_linux\linux32\steamcmd`
- `sdk\tools\ContentBuilder\builder_linux\linux32\steamerrorreporter`
- `sdk\tools\ContentBuilder\builder_linux\steamcmd.sh`
- `sdk\tools\ContentBuilder\builder_osx\crashhandler.dylib`
- `sdk\tools\ContentBuilder\builder_osx\steamcmd`
- `sdk\tools\ContentBuilder\builder_osx\steamcmd.sh`
- `sdk\tools\ContentBuilder\content\your game content lives here.txt`
- `sdk\tools\ContentBuilder\output\for build logs and intermediate files.txt`
- `sdk\tools\ContentBuilder\readme.txt`
- `sdk\tools\ContentBuilder\run_build.bat`
- `sdk\tools\ContentBuilder\scripts\app_build_1000.vdf`
- `sdk\tools\ContentBuilder\scripts\depot_build_1001.vdf`
- `sdk\tools\ContentBuilder\scripts\depot_build_1002.vdf`
- `sdk\tools\ContentBuilder\scripts\simple_app_build.vdf`
- `sdk\tools\ContentPrep.zip`
- `sdk\tools\ContentServer\htdocs\index.html`
- `sdk\tools\ContentServer\mongoose-3.1.exe`
- `sdk\tools\ContentServer\mongoose-license.txt`
- `sdk\tools\ContentServer\mongoose.conf`
- `sdk\tools\SteamPipeGUI.zip`
- `sdk\tools\codesigning\steam_modulesigning.public`
- `sdk\tools\goldmaster\disk_assets\481_depotcache_1.csd`
- `sdk\tools\goldmaster\disk_assets\481_depotcache_1.csm`
- `sdk\tools\goldmaster\disk_assets\Setup.exe`
- `sdk\tools\goldmaster\disk_assets\SteamRetailInstaller.dmg`
- `sdk\tools\goldmaster\disk_assets\SteamSetup.exe`
- `sdk\tools\goldmaster\disk_assets\autorun.inf`
- `sdk\tools\goldmaster\disk_assets\icon.ico`
- `sdk\tools\goldmaster\disk_assets\resources\click.wav`
- `sdk\tools\goldmaster\disk_assets\resources\eula.rtf`
- `sdk\tools\goldmaster\disk_assets\resources\hover.wav`
- `sdk\tools\goldmaster\disk_assets\resources\launch.wav`
- `sdk\tools\goldmaster\disk_assets\resources\readme.txt`
- `sdk\tools\goldmaster\disk_assets\resources\setup.bmp`
- `sdk\tools\goldmaster\disk_assets\resources\setup_arabic.ini`
- `sdk\tools\goldmaster\disk_assets\resources\setup_brazilian.ini`
- `sdk\tools\goldmaster\disk_assets\resources\setup_bulgarian.ini`
- `sdk\tools\goldmaster\disk_assets\resources\setup_czech.ini`
- `sdk\tools\goldmaster\disk_assets\resources\setup_danish.ini`
- `sdk\tools\goldmaster\disk_assets\resources\setup_dutch.ini`
- `sdk\tools\goldmaster\disk_assets\resources\setup_english.ini`
- `sdk\tools\goldmaster\disk_assets\resources\setup_finnish.ini`
- `sdk\tools\goldmaster\disk_assets\resources\setup_french.ini`
- `sdk\tools\goldmaster\disk_assets\resources\setup_german.ini`
- `sdk\tools\goldmaster\disk_assets\resources\setup_greek.ini`
- `sdk\tools\goldmaster\disk_assets\resources\setup_hungarian.ini`
- `sdk\tools\goldmaster\disk_assets\resources\setup_italian.ini`
- `sdk\tools\goldmaster\disk_assets\resources\setup_japanese.ini`
- `sdk\tools\goldmaster\disk_assets\resources\setup_koreana.ini`
- `sdk\tools\goldmaster\disk_assets\resources\setup_norwegian.ini`
- `sdk\tools\goldmaster\disk_assets\resources\setup_polish.ini`
- `sdk\tools\goldmaster\disk_assets\resources\setup_portuguese.ini`
- `sdk\tools\goldmaster\disk_assets\resources\setup_romanian.ini`
- `sdk\tools\goldmaster\disk_assets\resources\setup_russian.ini`
- `sdk\tools\goldmaster\disk_assets\resources\setup_schinese.ini`
- `sdk\tools\goldmaster\disk_assets\resources\setup_spanish.ini`
- `sdk\tools\goldmaster\disk_assets\resources\setup_swedish.ini`
- `sdk\tools\goldmaster\disk_assets\resources\setup_tchinese.ini`
- `sdk\tools\goldmaster\disk_assets\resources\setup_thai.ini`
- `sdk\tools\goldmaster\disk_assets\resources\setup_turkish.ini`
- `sdk\tools\goldmaster\disk_assets\resources\setup_ukrainian.ini`
- `sdk\tools\goldmaster\disk_assets\setup.ini`
- `sdk\tools\goldmaster\disk_assets\sku.sis`
- `sdk\tools\goldmaster\disk_assets\splash.tga`
- `sdk\tools\goldmaster\project_example.bat`
- `sdk\tools\goldmaster\sku_project_example.txt`
- `sdk\tools\linux\README.md`
- `test_launch.log`
- `tools\upx\upx-5.0.2-win64\COPYING`
- `tools\upx\upx-5.0.2-win64\LICENSE`
- `tools\upx\upx-5.0.2-win64\NEWS`
- `tools\upx\upx-5.0.2-win64\README`
- `tools\upx\upx-5.0.2-win64\THANKS.txt`
- `tools\upx\upx-5.0.2-win64\upx-doc.html`
- `tools\upx\upx-5.0.2-win64\upx-doc.txt`
- `tools\upx\upx-5.0.2-win64\upx.1`
- `tools\upx\upx-5.0.2-win64\upx.exe`
- `user_config.json`


## Detailed Module Analyses


## Module `Analyze_folders.py`

```python
import os

def analyze_folders(start_path):
    script_name = os.path.basename(__file__)  # Get script file name
    analyze_file = os.path.join(start_path, "analyze.txt")  # Output file path

    with open(analyze_file, "w", encoding="utf-8") as file:
        file.write(f"Folder Analysis Report\n")
        file.write(f"{'='*50}\n\n")
        file.write(f"Root Directory: {start_path}\n\n")
        
        for root, dirs, files in os.walk(start_path):
            # Skip directories named 'venv'
            if "venv" in root.split(os.sep):
                continue

            level = root.replace(start_path, "").count(os.sep)
            indent = "|   " * level  # Tree structure formatting
            file.write(f"{indent}|-- {os.path.basename(root)}/\n")

            # Filter out the script and output file from the list of files
            filtered_files = [f for f in files if f not in {script_name, "analyze.txt"}]

            # List files in the directory
            for f in filtered_files:
                file_indent = "|   " * (level + 1)
                file.write(f"{file_indent}|-- {f}\n")
    
    print(f"Analysis complete. Results saved in {analyze_file}")

if __name__ == "__main__":
    script_directory = os.path.dirname(os.path.abspath(__file__))
    analyze_folders(script_directory)
```

**Functions:** analyze_folders(start_path)


## Module `ico_converter.py`

```python
#!/usr/bin/env python3
# ico_converter.py — Convert PNG/JPG to ICO with GUI & persistent config
# Automatically creates inbound and outbound folders and renames output automatically

import sys, os, json, traceback
from pathlib import Path
from PIL import Image

from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThread
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFileDialog, QTextEdit, QProgressBar,
    QMessageBox, QLineEdit, QGroupBox, QFormLayout
)

# Script root paths
SCRIPT_ROOT = Path(__file__).parent.resolve()
INBOUND_FOLDER = SCRIPT_ROOT / "Ico Inbound"
OUTBOUND_FOLDER = SCRIPT_ROOT / "Ico Outbound"
CONFIG_FILE = SCRIPT_ROOT / "ico_converter_config.json"

# ───────────────────────────────────────────────
# Background worker
# ───────────────────────────────────────────────
class Worker(QObject):
    log = pyqtSignal(str)
    prog = pyqtSignal(int)
    done = pyqtSignal()
    err = pyqtSignal(str)
    icon_name = "MyGameIcon"

    def __init__(self, inbound_folder):
        super().__init__()
        self.inbound_folder = Path(inbound_folder)

    def run(self):
        try:
            # Collect images
            images = list(self.inbound_folder.glob("*.png")) + list(self.inbound_folder.glob("*.jpg"))
            if not images:
                raise FileNotFoundError("No PNG or JPG files found in inbound folder.")

            OUTBOUND_FOLDER.mkdir(exist_ok=True)

            # Use only first image
            img_path = images[0]
            self.log.emit(f"Processing: {img_path.name}")
            try:
                img = Image.open(img_path)
                ico_path = OUTBOUND_FOLDER / f"{self.icon_name}.ico"
                img.save(ico_path, format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
                self.log.emit(f"Created Icon: {self.icon_name}")
            except Exception as e:
                self.log.emit(f"Error converting {img_path.name}: {e}")

            self.prog.emit(100)
            self.done.emit()

        except Exception:
            tb = traceback.format_exc()
            self.err.emit(tb)

# ───────────────────────────────────────────────
# Main Window
# ───────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ICO Converter")
        self.setWindowIcon(QIcon())
        self.setMinimumSize(700, 550)

        # Ensure inbound & outbound folders exist
        INBOUND_FOLDER.mkdir(exist_ok=True)
        OUTBOUND_FOLDER.mkdir(exist_ok=True)

        self.config = self.load_config()

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Settings group
        settings_group = QGroupBox("Settings")
        settings_layout = QFormLayout(settings_group)

        # Icon name input
        self.icon_name_input = QLineEdit(self.config.get("icon_name", "MyGameIcon"))
        settings_layout.addRow("Output Icon Name:", self.icon_name_input)

        # Inbound folder input
        self.inbound_path = QLineEdit(self.config.get("inbound_folder", str(INBOUND_FOLDER)))
        btn_browse_inbound = QPushButton("Browse")
        btn_browse_inbound.clicked.connect(self.browse_inbound)
        inbound_layout = QHBoxLayout()
        inbound_layout.addWidget(self.inbound_path)
        inbound_layout.addWidget(btn_browse_inbound)
        settings_layout.addRow("Inbound Folder:", inbound_layout)

        layout.addWidget(settings_group)

        # Start button & progress bar
        start_layout = QHBoxLayout()
        self.btn_start = QPushButton("Start Conversion")
        self.btn_start.clicked.connect(self.start_conversion)
        self.progress = QProgressBar()
        start_layout.addWidget(self.btn_start)
        start_layout.addWidget(self.progress)
        layout.addLayout(start_layout)

        # Console
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setFont(QFont("Consolas", 10))
        layout.addWidget(self.console)

        self.thread = None

    def browse_inbound(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Inbound Folder", self.inbound_path.text())
        if folder:
            self.inbound_path.setText(folder)
            self.save_config()

    def start_conversion(self):
        inbound_folder = self.inbound_path.text().strip()
        icon_name = self.icon_name_input.text().strip()

        if not inbound_folder or not Path(inbound_folder).exists():
            QMessageBox.warning(self, "Invalid Path", "Please select a valid inbound folder.")
            return
        if not icon_name:
            QMessageBox.warning(self, "Invalid Name", "Please provide an output icon name.")
            return

        self.console.clear()
        self.progress.setValue(0)
        self.save_config()

        self.thread = QThread()
        self.worker = Worker(inbound_folder)
        self.worker.icon_name = icon_name
        self.worker.log.connect(self.log)
        self.worker.prog.connect(self.progress.setValue)
        self.worker.done.connect(lambda: self.on_done(icon_name))
        self.worker.err.connect(self.show_error)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.thread.start()

    def on_done(self, icon_name):
        QMessageBox.information(self, "Done", f"Icon created successfully:\n{icon_name}")

    def log(self, message):
        self.console.append(message)

    def show_error(self, error_text):
        dialog = QMessageBox(self)
        dialog.setIcon(QMessageBox.Critical)
        dialog.setWindowTitle("Error")
        dialog.setText("An error occurred during processing:")
        details = QTextEdit()
        details.setPlainText(error_text)
        details.setReadOnly(True)
        details.setMaximumHeight(300)
        layout = dialog.layout()
        layout.addWidget(details, layout.rowCount(), 0, 1, layout.columnCount())
        copy_btn = dialog.addButton("Copy Error", QMessageBox.ActionRole)
        copy_btn.clicked.connect(lambda: QApplication.clipboard().setText(error_text))
        dialog.addButton("Close", QMessageBox.RejectRole)
        dialog.exec_()

    def load_config(self):
        if CONFIG_FILE.exists():
            try:
                return json.loads(CONFIG_FILE.read_text())
            except:
                pass
        return {}

    def save_config(self):
        self.config["inbound_folder"] = self.inbound_path.text().strip()
        self.config["icon_name"] = self.icon_name_input.text().strip()
        CONFIG_FILE.write_text(json.dumps(self.config, indent=2))

# ───────────────────────────────────────────────
def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
```

**Classes:** Worker, MainWindow
**Functions:** main()


## Module `OLD_game_packager.py`

```python
#!/usr/bin/env python3
# game_packager.py  —  Enhanced version with project selection, original game folder cloning, prompt management, and snapshot generation

r"""
Enhanced Panda3D packager / auditor / Steam uploader GUI.

New Features:
• Project folder selection with dropdown menu from C:\\Users\\Art PC\\Desktop\\Custom_Compiler\\Projects
• Original game folder input with cloning to prevent tampering
• Enhanced tooltips for all settings with 3-second delay
• Prompt management system with Ollama integration
• Default prompt templates auto-creation
• Improved project structure display
• Enhanced Steam configuration with username and validation
• Integration with Steamworks SDK in sdk/ folder
• Full project snapshot generation with AI-powered analysis
• ISO generation
• oscdimg/mkisofs support
• Icon converter launcher
• UPX-path override
"""


import sys, os, json, shutil, subprocess, traceback
from pathlib import Path
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QThread, QDir
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QLabel, QPushButton, QComboBox, QLineEdit, QTextEdit,
    QCheckBox, QProgressBar, QMessageBox, QTabWidget, QGroupBox, QFormLayout,
    QInputDialog, QTreeView, QFileSystemModel, QStyle, QProxyStyle, QToolTip,
    QHeaderView, QFileDialog, QListWidget, QTextBrowser
)


# ─────────────────────────────────────────────────────────────────────────────
class SlowTipStyle(QProxyStyle):
    """Delay tool-tips by 3 seconds."""
    def styleHint(self, hint, option=None, widget=None, returnData=None):
        if hint == QStyle.SH_ToolTip_WakeUpDelay:
            return 3000
        return super().styleHint(hint, option, widget, returnData)

# ─────────────────────────────────────────────────────────────────────────────
def create_default_prompts(prompts_dir: Path):
    """Create default prompt templates in the prompts directory."""
    prompts_dir.mkdir(exist_ok=True)
    
    default_prompts = {
        "code_analysis.txt": """Analyze this Panda3D project for potential issues:

1. Check for common Panda3D antipatterns
2. Identify performance bottlenecks
3. Look for resource management issues
4. Check for proper scene graph usage
5. Identify potential memory leaks

Project structure:
{project_structure}

Main issues found:
{audit_results}

Please provide specific recommendations for improvement.""",

        "build_optimization.txt": """Review this Panda3D project for build optimization:

1. Suggest PyInstaller optimizations
2. Recommend asset compression strategies  
3. Identify unnecessary dependencies
4. Suggest code minification approaches
5. Review packaging structure

Project details:
{project_structure}

Build configuration:
{build_config}

Provide actionable optimization suggestions.""",

        "deployment_checklist.txt": """Create a deployment checklist for this Panda3D game:

1. Verify all assets are included
2. Check Steam integration setup
3. Validate system requirements
4. Review distribution file structure
5. Test cross-platform compatibility

Project configuration:
{project_config}

Generate a comprehensive pre-deployment checklist.""",

        "security_audit.txt": """Perform a security audit of this Panda3D project:

1. Check for exposed API keys or secrets
2. Validate input sanitization
3. Review network communication security
4. Check file access permissions
5. Identify potential injection vulnerabilities

Audit findings:
{audit_results}

Provide security recommendations and fixes."""
    }
    
    for filename, content in default_prompts.items():
        prompt_file = prompts_dir / filename
        if not prompt_file.exists():
            prompt_file.write_text(content, encoding='utf-8')

# ─────────────────────────────────────────────────────────────────────────────
def audit_project(project_dir: Path):
    """Enhanced static audit with more comprehensive checks."""
    results = []
    
    # Check if valid Panda3D project
    main_files = ['main.py', 'game.py', 'app.py']
    has_main = any((project_dir / f).exists() for f in main_files)
    if not has_main:
        results.append(("WARNING", "No main entry point found (main.py, game.py, or app.py)"))
    else:
        results.append(("INFO", "Entry point detected"))
    
    # Mixed GUI frameworks check
    tk_use = qt_use = pd_use = False
    python_files = []
    for py_file in project_dir.rglob("*.py"):
        if any(part in py_file.parts for part in ["venv", "__pycache__", ".git"]):
            continue
        python_files.append(py_file)
        try:
            txt = py_file.read_text(errors="ignore")
            tk_use |= "import tkinter" in txt or "from tkinter" in txt
            qt_use |= "from PyQt" in txt or "import PyQt" in txt
            pd_use |= "from direct.gui" in txt or "from panda3d" in txt
        except:
            continue
    
    if qt_use and (tk_use or pd_use):
        results.append(("WARNING", "Mixed GUI frameworks detected - may cause conflicts"))
    else:
        results.append(("INFO", "GUI framework compatibility OK"))

    # Panda3D specific checks
    if pd_use:
        results.append(("INFO", f"Panda3D imports found in {len([f for f in python_files if 'panda3d' in f.read_text(errors='ignore')])} files"))
    else:
        results.append(("WARNING", "No Panda3D imports detected - verify this is a Panda3D project"))

    # Asset directory checks
    asset_dirs = ['assets', 'models', 'textures', 'sounds', 'music']
    found_assets = [d for d in asset_dirs if (project_dir / d).exists()]
    if found_assets:
        results.append(("INFO", f"Asset directories found: {', '.join(found_assets)}"))
    else:
        results.append(("WARNING", "No standard asset directories found"))

    # Scene modules
    scene_modules = []
    scenes_dir = project_dir / "scenes"
    if scenes_dir.exists():
        for f in scenes_dir.rglob("*.py"):
            if any(part in f.parts for part in ["venv", "__pycache__"]):
                continue
            rel = f.relative_to(project_dir).with_suffix("")
            scene_modules.append(str(rel).replace(os.sep, "."))
        results.append(("INFO", f"{len(scene_modules)} scene modules found"))
    else:
        results.append(("WARNING", "No scenes/ directory found"))

    # Configuration files
    config_files = [f for f in project_dir.rglob("*.json") if "venv" not in f.parts]
    config_files.extend([f for f in project_dir.rglob("*.yaml") if "venv" not in f.parts])
    config_files.extend([f for f in project_dir.rglob("*.ini") if "venv" not in f.parts])
    if config_files:
        results.append(("INFO", f"{len(config_files)} configuration files detected"))
    else:
        results.append(("WARNING", "No configuration files detected"))

    # API key exposure check
    sensitive_patterns = ['sk-', 'api_key', 'secret_key', 'password', 'token']
    exposed_file = None
    for txt_file in project_dir.rglob("*.txt"):
        if any(part in txt_file.parts for part in ["venv", "__pycache__"]):
            continue
        try:
            content = txt_file.read_text(errors="ignore").lower()
            if any(pattern in content for pattern in sensitive_patterns):
                exposed_file = txt_file.relative_to(project_dir)
                break
        except:
            continue
    
    if exposed_file:
        results.append(("ERROR", f"Potential sensitive data in {exposed_file}"))
    else:
        results.append(("INFO", "No obvious sensitive data exposure detected"))

    # Resource bundling check
    main_candidates = [project_dir / f for f in main_files if (project_dir / f).exists()]
    has_resource_wrapper = False
    for main_file in main_candidates:
        try:
            content = main_file.read_text(errors="ignore")
            if "sys._MEIPASS" in content or "getattr(sys, '_MEIPASS'" in content:
                has_resource_wrapper = True
                break
        except:
            continue
    
    if has_resource_wrapper:
        results.append(("INFO", "Resource bundling wrapper detected"))
    else:
        results.append(("WARNING", "No PyInstaller resource wrapper found - may cause asset loading issues"))

    # Dependencies check
    req_files = list(project_dir.glob("requirements*.txt"))
    if req_files:
        results.append(("INFO", f"Requirements files found: {[f.name for f in req_files]}"))
    else:
        results.append(("WARNING", "No requirements.txt found - dependencies may not be tracked"))

    return results, scene_modules

# ─────────────────────────────────────────────────────────────────────────────
def generate_project_snapshot(root_path: Path, include_hidden=False) -> str:
    """Generate a formatted text tree of the project structure, excluding specified patterns."""
    try:
        # Initialize counters for summary
        file_count = 0
        folder_count = 0
        python_files = 0
        asset_files = 0
        config_files = 0
        total_size = 0
        lines = []
        max_entries = 2000
        entry_count = 0

        # Define asset and config extensions
        asset_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tga', '.ogg', '.wav', '.mp3', '.bam', '.egg', '.gltf', '.fbx'}
        config_extensions = {'.json', '.yaml', '.ini'}

        # Define exclusions
        exclude_dirs = {'venv', '__pycache__', '.git', '.idea'}
        exclude_files = {'.gitignore', '.gitattributes', '.DS_Store'}

        # Check if temporary snapshot exists
        snapshot_file = root_path / ".last_snapshot.txt"
        if snapshot_file.exists():
            try:
                content = snapshot_file.read_text(encoding='utf-8')
                lines = content.splitlines()
                summary_line = lines[-1] if lines else ""
                if summary_line.startswith("Summary:"):
                    return content
            except:
                pass  # Regenerate if temp file is invalid

        lines.append(f"Project Snapshot: {root_path.name}\n")

        # Walk the directory
        for root, dirs, files in os.walk(root_path, followlinks=False):
            # Skip excluded directories
            if not include_hidden:
                dirs[:] = [d for d in dirs if not (d.startswith('.') or d in exclude_dirs)]
            else:
                dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            # Get relative path and indentation level
            rel_root = Path(root).relative_to(root_path)
            level = len(rel_root.parts) if rel_root != Path(".") else 0
            indent = "  " * level

            # Add folder
            folder_name = rel_root.name if rel_root != Path(".") else root_path.name
            lines.append(f"{indent}{folder_name}/")
            folder_count += 1
            entry_count += 1

            # Process files
            sub_indent = "  " * (level + 1)
            for file in sorted(files):
                if not include_hidden and (file.startswith('.') or file in exclude_files or file.endswith('.pyc')):
                    continue
                if include_hidden and (file in exclude_files or file.endswith('.pyc')):
                    continue
                
                file_path = Path(root) / file
                try:
                    file_size = file_path.stat().st_size
                    lines.append(f"{sub_indent}{file} ({file_size} bytes)")
                    file_count += 1
                    total_size += file_size
                    entry_count += 1

                    # Count file types for summary
                    if file_path.suffix.lower() == '.py':
                        python_files += 1
                    elif file_path.suffix.lower() in asset_extensions:
                        asset_files += 1
                    elif file_path.suffix.lower() in config_extensions:
                        config_files += 1

                except (PermissionError, OSError) as e:
                    lines.append(f"{sub_indent}{file} (access error: {str(e)})")
                    file_count += 1
                    entry_count += 1

                if entry_count >= max_entries:
                    lines.append(f"{indent}  ... (truncated at {max_entries} entries)")
                    break
            
            if entry_count >= max_entries:
                break

        # Add summary
        summary = (f"Summary: {file_count} files, {folder_count} folders, "
                  f"{python_files} Python files, {asset_files} assets, "
                  f"{config_files} config files, total size {total_size} bytes")
        lines.append(summary)

        # Save snapshot to temporary file
        snapshot_content = '\n'.join(lines)
        try:
            snapshot_file.write_text(snapshot_content, encoding='utf-8')
        except Exception as e:
            print(f"Failed to save snapshot: {e}")  # Silent fail to avoid disrupting main flow

        return snapshot_content

    except Exception as e:
        raise Exception(f"Failed to generate project snapshot: {str(e)}")

# ─────────────────────────────────────────────────────────────────────────────
class Worker(QObject):
    """Background worker emitting log/progress/done/error signals."""
    log = pyqtSignal(str)
    prog = pyqtSignal(int)
    done = pyqtSignal()
    err = pyqtSignal(str)

    def __init__(self, func, *args):
        super().__init__()
        self.func = func
        self.args = args

    def run(self):
        try:
            self.func(self, *self.args)
            self.done.emit()
        except Exception:
            tb = traceback.format_exc()
            self.log.emit(f"<span style='color:red'>ERROR:<br>{tb}</span>")
            self.err.emit(tb)

# ─────────────────────────────────────────────────────────────────────────────
class MainWindow(QMainWindow):
    CONFIG = ".game_tool_config.json"
    PROJECTS_DIR = Path(r"C:\\Users\\Art PC\\Desktop\\Custom_Compiler\\Projects")
    SDK_DIR = Path(__file__).parent / "sdk"

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enhanced Panda3D Game Packager")
        self.setWindowIcon(QIcon.fromTheme("applications-games"))
        self.setMinimumSize(1000, 900)
        QApplication.setStyle(SlowTipStyle())
        QToolTip.setFont(QFont("Sans", 10))

        # Application directories
        self.app_root = Path(__file__).parent.resolve()
        self.prompts_dir = self.app_root / "prompts"
        
        # Create default prompts on first run
        create_default_prompts(self.prompts_dir)

        # Project state
        self.project_root = None
        self.build_output_dir = None
        self.original_game_dir = None
        self.clone_dir = None
        self.cfg = {}
        self.include_hidden_files = False  # For snapshot generation

        self._init_ui()
        self._load_models()

    def _init_ui(self):
        """Initialize all UI components, layouts, and styling."""
        self.setStyleSheet("""
            QWidget { background: #444; color: #eee; font-family: Sans; }
            QTabBar::tab { background: #333; color: #eee; padding: 8px 12px; margin: 1px; }
            QTabBar::tab:selected { background: #006666; font-weight: bold; }
            QPushButton { background: #006666; color: #fff; border-radius: 4px; padding: 6px 12px; font-weight: bold; }
            QPushButton:disabled { background: #333; color: #888; }
            QPushButton:hover:!disabled { background: #008888; }
            QLineEdit, QComboBox, QTextEdit { background: #333; color: #eee; border: 1px solid #555; padding: 4px; }
            QLineEdit:focus, QComboBox:focus { border: 2px solid #00cc66; }
            QProgressBar { background: #333; border: 1px solid #555; color: #fff; text-align: center; }
            QProgressBar::chunk { background: #00cc66; }
            QToolTip { background-color: #222; color: #fff; border: 1px solid #00cc66; padding: 6px; }
            QHeaderView::section { background-color: #333; color: #eee; border: 1px solid #555; padding: 4px; }
            QGroupBox { font-weight: bold; border: 2px solid #555; margin-top: 1ex; padding-top: 10px; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px 0 5px; }
            QListWidget { background: #333; color: #eee; border: 1px solid #555; }
            QListWidget::item:selected { background: #006666; }
        """)

        central = QWidget(self)
        self.setCentralWidget(central)
        main_v = QVBoxLayout(central)

        # Project selection bar
        project_bar = QHBoxLayout()
        
        project_label = QLabel("Select Project:")
        self._tip(project_label, "Choose a project folder from the projects directory")
        project_bar.addWidget(project_label)
        
        self.cmb_project = QComboBox()
        self._tip(self.cmb_project, "Select a Panda3D project folder from C:\\Users\\Art PC\\Desktop\\Custom_Compiler\\Projects")
        self.cmb_project.addItem("Select a project...")
        self._populate_project_dropdown()
        self.cmb_project.currentIndexChanged.connect(self._select_project_folder)
        project_bar.addWidget(self.cmb_project)
        
        self.lbl_project_path = QLabel("No project selected")
        self._tip(self.lbl_project_path, "Displays the selected project folder path")
        self.lbl_project_path.setStyleSheet("color: #ccc; font-style: italic; padding: 6px;")
        project_bar.addWidget(self.lbl_project_path, 1)
        
        project_bar.addWidget(QLabel("AI Model:"))
        self.cmb_model = QComboBox()
        self._tip(self.cmb_model, "Select the Ollama model for AI-powered project analysis")
        project_bar.addWidget(self.cmb_model)

        main_v.addLayout(project_bar)

        # Tabs
        self.tabs = QTabWidget()
        main_v.addWidget(self.tabs, 2)
        self._build_tab_project()
        self._build_tab_build()
        self._build_tab_prompts()
        self._build_tab_upload()

        # File trees splitter
        splitter = QSplitter(Qt.Horizontal)
        self.tree_proj = self._make_tree("Project Structure", "Browse your project files and folders")
        self.tree_build = self._make_tree("Build Output", "View the generated build files and packages")
        splitter.addWidget(self.tree_proj)
        splitter.addWidget(self.tree_build)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        main_v.addWidget(splitter, 1)

        # Actions Console
        console_label = QLabel("Actions Console:")
        self._tip(console_label, "Log of all operations, including status messages and errors")
        console_label.setStyleSheet("font-weight: bold; color: #00cc66;")
        main_v.addWidget(console_label)
        self.console = QTextEdit(readOnly=True)
        self._tip(self.console, "Displays live logs of operations, including detailed status messages and errors")
        self.console.setMaximumHeight(200)
        main_v.addWidget(self.console)

    def _tip(self, widget, text):
        """Attach a 3-second delayed tooltip."""
        widget.setToolTip(text)
        widget.setAttribute(Qt.WA_AlwaysShowToolTips)

    def _make_tree(self, title, tip):
        """Create a file-tree panel with stretched Name column."""
        box = QGroupBox(title)
        self._tip(box, tip)
        lay = QVBoxLayout(box)
        model = QFileSystemModel()
        model.setRootPath("")
        tree = QTreeView()
        tree.setModel(model)
        tree.setAnimated(True)
        # Hide size, type, and date columns
        for col in range(1, model.columnCount()):
            tree.hideColumn(col)
        tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        lay.addWidget(tree)
        box.model, box.tree = model, tree
        return box

    def _populate_project_dropdown(self):
        """Populate the project dropdown with folders from PROJECTS_DIR."""
        if not self.PROJECTS_DIR.exists():
            self._log(f"<span style='color:orange'>Projects directory not found: {self.PROJECTS_DIR}</span>")
            return
        
        for folder in self.PROJECTS_DIR.iterdir():
            if folder.is_dir():
                self.cmb_project.addItem(folder.name, str(folder))

    def _select_project_folder(self):
        """Handle project selection from dropdown."""
        index = self.cmb_project.currentIndex()
        if index <= 0:  # "Select a project..." or no selection
            self.project_root = None
            self.build_output_dir = None
            self.original_game_dir = None
            self.clone_dir = None
            self.lbl_project_path.setText("No project selected")
            self.lbl_project_path.setStyleSheet("color: #ccc; font-style: italic; padding: 6px;")
            if 'original_game_dir' in self._widgets:
                self._widgets['original_game_dir'].setText("")
            self._refresh_trees()
            return
        
        folder = self.cmb_project.itemData(index)
        if folder:
            self.project_root = Path(folder)
            self.build_output_dir = self.project_root / "build_output"
            self.clone_dir = self.project_root / "clone"
            self.build_output_dir.mkdir(exist_ok=True)
            
            # Update UI
            self.lbl_project_path.setText(f"Project: {self.project_root.name} ({str(self.project_root)})")
            self.lbl_project_path.setStyleSheet("color: #00cc66; font-weight: bold; padding: 6px;")
            
            # Load or create config
            self._load_project_config()
            
            # Update original game dir if stored in config
            if self.cfg.get('original_game_dir'):
                self.original_game_dir = Path(self.cfg['original_game_dir'])
                if 'original_game_dir' in self._widgets:
                    self._widgets['original_game_dir'].setText(str(self.original_game_dir))
            
            # Refresh file trees
            self._refresh_trees()
            
            self._log(f"<span style='color:lightgreen'>Project loaded: {self.project_root}</span>")
            self._log(f"<span style='color:cyan'>Build output directory: {self.build_output_dir}</span>")
            if self.original_game_dir:
                self._log(f"<span style='color:cyan'>Original game directory: {self.original_game_dir}</span>")

    def _load_project_config(self):
        """Load project configuration or create default."""
        config_file = self.project_root / self.CONFIG
        
        if config_file.exists():
            try:
                self.cfg = json.loads(config_file.read_text())
                self._log("<span style='color:cyan'>Loaded existing project configuration</span>")
            except json.JSONDecodeError:
                self._log("<span style='color:orange'>Invalid config file, creating new one</span>")
                self._create_default_config()
        else:
            self._create_default_config()
        
        # Update UI fields
        self._update_ui_from_config()

    def _create_default_config(self):
        """Create default project configuration."""
        # Try to detect entry script in clone directory if it exists
        entry_candidates = ['main.py', 'game.py', 'app.py']
        entry_script = "main.py"  # default
        if self.clone_dir and self.clone_dir.exists():
            for candidate in entry_candidates:
                if (self.clone_dir / candidate).exists():
                    entry_script = candidate
                    break
        elif self.original_game_dir and self.original_game_dir.exists():
            for candidate in entry_candidates:
                if (self.original_game_dir / candidate).exists():
                    entry_script = candidate
                    break
        
        self.cfg = {
            "entry_script": entry_script,
            "game_name": self.project_root.name if self.project_root else "Game",
            "original_game_dir": "",
            "encrypt_code": False,
            "use_nuitka": False,
            "compress_upx": False,
            "do_zip": True,
            "steam_appid": "",
            "steam_depot_id": "",
            "steam_username": "",
            "cb_path": str(self.SDK_DIR / "tools" / "ContentBuilder") if (self.SDK_DIR / "tools" / "ContentBuilder").exists() else "",
            "extra_assets": [],
            "exclude_modules": [],
            "icon_path": "",
            "include_hidden_files": False,  # New config for hidden files in snapshot
            "iso_label": "MyGameISO",
            "create_iso": False,
            "oscdimg_path": "",
            "upx_path": ""
        }
        self._save_config()

    def _save_config(self):
        """Save current configuration to project folder."""
        if not self.project_root:
            return
        
        config_file = self.project_root / self.CONFIG
        config_file.write_text(json.dumps(self.cfg, indent=2))
        self._log("<span style='color:cyan'>Configuration saved</span>")

    def _update_config_from_ui(self):
        """Update config from UI fields."""
        for key, widget in self._widgets.items():
            if isinstance(widget, QLineEdit):
                self.cfg[key] = widget.text().strip()
            elif isinstance(widget, QCheckBox):
                self.cfg[key] = widget.isChecked()
            elif isinstance(widget, QComboBox):
                self.cfg[key] = widget.currentText().strip()

    def _update_ui_from_config(self):
        """Update UI fields from current config."""
        for key, widget in self._widgets.items():
            value = self.cfg.get(key, "")
            if isinstance(widget, QLineEdit):
                widget.setText(str(value))
            elif isinstance(widget, QCheckBox):
                widget.setChecked(bool(value))
            elif isinstance(widget, QComboBox):
                idx = widget.findText(str(value))
                if idx >= 0:
                    widget.setCurrentIndex(idx)

    def _load_models(self):
        """Load Ollama models."""
        models = []
        try:
            result = subprocess.run(["ollama", "list"], 
                                  capture_output=True, text=True, check=True)
            for line in result.stdout.splitlines()[1:]:  # Skip header
                parts = line.split()
                if parts:
                    models.append(parts[0])
        except (subprocess.CalledProcessError, FileNotFoundError):
            self._log("<span style='color:orange'>Ollama not found or no models available</span>")
        
        if not models:
            models = ["phi4:latest", "llama3.2:latest", "qwen2.5:latest"]
        
        self.cmb_model.addItems(models)
        # Set default to phi4:latest if available
        idx = self.cmb_model.findText("phi4:latest")
        if idx >= 0:
            self.cmb_model.setCurrentIndex(idx)

    def _build_tab_project(self):
        """Build the Project configuration tab."""
        tab = QWidget()
        self.tabs.addTab(tab, "Project")
        layout = QVBoxLayout(tab)

        self._widgets = {}

        # Diagnosis section
        diag_group = QGroupBox("Pre-Build Diagnosis")
        self._tip(diag_group, "Tools to analyze your project before building")
        diag_layout = QVBoxLayout(diag_group)
        
        btn_diag = QPushButton("Run Pre-Build Diagnosis")
        self._tip(btn_diag, "Analyze project structure, dependencies, and code quality using AI")
        btn_diag.clicked.connect(self._run_diagnosis)
        diag_layout.addWidget(btn_diag)
        
        self._widgets['include_hidden_files'] = QCheckBox("Include Hidden Files in Snapshot")
        self._tip(self._widgets['include_hidden_files'], "Include hidden files and folders in the project snapshot (optional)")
        self._widgets['include_hidden_files'].stateChanged.connect(self._on_setting_changed)
        diag_layout.addWidget(self._widgets['include_hidden_files'])
        
        self.pb_diag = QProgressBar()
        self._tip(self.pb_diag, "Shows progress of the diagnosis process")
        diag_layout.addWidget(self.pb_diag)
        
        layout.addWidget(diag_group)

        # Project settings
        settings_group = QGroupBox("Project Settings")
        self._tip(settings_group, "Configure essential project settings for building your game")
        settings_form = QFormLayout(settings_group)
        
        # Original game directory
        orig_game_layout = QHBoxLayout()
        self._widgets['original_game_dir'] = QLineEdit()
        self._tip(self._widgets['original_game_dir'], "Path to the original game folder containing all Python scripts and assets (will be cloned to prevent modification)")
        self._widgets['original_game_dir'].textChanged.connect(self._on_setting_changed)
        orig_browse_btn = QPushButton("Browse")
        self._tip(orig_browse_btn, "Select the original game folder containing your game files")
        orig_browse_btn.clicked.connect(self._browse_original_game_dir)
        orig_open_btn = QPushButton("Open")
        self._tip(orig_open_btn, "Open the original game folder in the file explorer")
        orig_open_btn.clicked.connect(self._open_original_game_dir)
        orig_game_layout.addWidget(self._widgets['original_game_dir'])
        orig_game_layout.addWidget(orig_browse_btn)
        orig_game_layout.addWidget(orig_open_btn)
        settings_form.addRow("Original Game Folder:", orig_game_layout)
        
        # Entry script
        self._widgets['entry_script'] = QLineEdit()
        self._tip(self._widgets['entry_script'], "Main Python file that starts your game (e.g., main.py)")
        self._widgets['entry_script'].textChanged.connect(self._on_setting_changed)
        settings_form.addRow("Entry Script:", self._widgets['entry_script'])
        
        # Game name
        self._widgets['game_name'] = QLineEdit()
        self._tip(self._widgets['game_name'], "Display name for your game - used for executable naming")
        self._widgets['game_name'].textChanged.connect(self._on_setting_changed)
        settings_form.addRow("Game Title:", self._widgets['game_name'])
        
        # Icon path
        icon_layout = QHBoxLayout()
        self._widgets['icon_path'] = QLineEdit()
        self._tip(self._widgets['icon_path'], "Path to .ico file for executable icon (optional)")
        icon_btn = QPushButton("Browse")
        self._tip(icon_btn, "Select an icon file for your executable")
        icon_btn.clicked.connect(self._browse_icon)
        icon_layout.addWidget(self._widgets['icon_path'])
        icon_layout.addWidget(icon_btn)
        settings_form.addRow("Icon File:", icon_layout)
        
        # Run Icon Converter button
        icon_converter_btn = QPushButton("Run Icon Converter →")
        self._tip(icon_converter_btn, "Launch the icon converter tool")
        icon_converter_btn.clicked.connect(self._run_icon_converter)
        settings_form.addRow("", icon_converter_btn)
        
        layout.addWidget(settings_group)
        
        # Packaging Options group
        packaging_group = QGroupBox("Packaging Options")
        self._tip(packaging_group, "Configure packaging and distribution options")
        packaging_form = QFormLayout(packaging_group)
        
        self._widgets['use_nuitka'] = QCheckBox()
        self._tip(self._widgets['use_nuitka'], "Use Nuitka compiler instead of PyInstaller for faster execution (experimental)")
        self._widgets['use_nuitka'].stateChanged.connect(self._on_setting_changed)
        packaging_form.addRow("Use Nuitka:", self._widgets['use_nuitka'])
        
        self._widgets['encrypt_code'] = QCheckBox()
        self._tip(self._widgets['encrypt_code'], "Encrypt Python bytecode using PyArmor to prevent reverse engineering")
        self._widgets['encrypt_code'].stateChanged.connect(self._on_setting_changed)
        packaging_form.addRow("Encrypt Code:", self._widgets['encrypt_code'])
        
        self._widgets['compress_upx'] = QCheckBox()
        self._tip(self._widgets['compress_upx'], "Compress executable with UPX to reduce file size (may trigger antivirus)")
        self._widgets['compress_upx'].stateChanged.connect(self._on_setting_changed)
        packaging_form.addRow("Compress with UPX:", self._widgets['compress_upx'])
        
        upx_layout = QHBoxLayout()
        self._widgets['upx_path'] = QLineEdit()
        self._tip(self._widgets['upx_path'], "Path to UPX directory")
        self._widgets['upx_path'].textChanged.connect(self._on_setting_changed)
        upx_browse = QPushButton("Browse")
        self._tip(upx_browse, "Select the UPX directory")
        upx_browse.clicked.connect(self._browse_upx)
        upx_layout.addWidget(self._widgets['upx_path'])
        upx_layout.addWidget(upx_browse)
        packaging_form.addRow("UPX Path:", upx_layout)
        
        self._widgets['do_zip'] = QCheckBox()
        self._tip(self._widgets['do_zip'], "Create a ZIP archive of the final build for easy distribution")
        self._widgets['do_zip'].stateChanged.connect(self._on_setting_changed)
        packaging_form.addRow("Create ZIP:", self._widgets['do_zip'])
        
        self._widgets['create_iso'] = QCheckBox()
        self._tip(self._widgets['create_iso'], "Generate ISO image")
        self._widgets['create_iso'].stateChanged.connect(self._on_setting_changed)
        packaging_form.addRow("Generate ISO:", self._widgets['create_iso'])
        
        self._widgets['iso_label'] = QLineEdit()
        self._tip(self._widgets['iso_label'], "Label for the ISO image")
        self._widgets['iso_label'].textChanged.connect(self._on_setting_changed)
        packaging_form.addRow("ISO Label:", self._widgets['iso_label'])
        
        oscdimg_layout = QHBoxLayout()
        self._widgets['oscdimg_path'] = QLineEdit()
        self._tip(self._widgets['oscdimg_path'], "Path to oscdimg.exe or mkisofs.exe for ISO creation")
        self._widgets['oscdimg_path'].textChanged.connect(self._on_setting_changed)
        oscdimg_browse = QPushButton("Browse")
        self._tip(oscdimg_browse, "Select the path to oscdimg.exe")
        oscdimg_browse.clicked.connect(self._browse_oscdimg)
        oscdimg_layout.addWidget(self._widgets['oscdimg_path'])
        oscdimg_layout.addWidget(oscdimg_browse)
        packaging_form.addRow("oscdimg Path:", oscdimg_layout)
        
        layout.addWidget(packaging_group)

    def _browse_oscdimg(self):
        """Browse for oscdimg.exe path."""
        file, _ = QFileDialog.getOpenFileName(self, "Select oscdimg.exe", "", "Executables (*.exe)")
        if file:
            self._widgets['oscdimg_path'].setText(file)
            self._on_setting_changed()

    def _browse_upx(self):
        """Browse for UPX directory."""
        folder = QFileDialog.getExistingDirectory(self, "Select UPX Directory")
        if folder:
            self._widgets['upx_path'].setText(folder)
            self._on_setting_changed()

    def _run_icon_converter(self):
        """Run the icon converter script."""
        self._update_config_from_ui()
        self._save_config()
        subprocess.Popen([sys.executable, "ico_converter.py"])

    def _browse_original_game_dir(self):
        """Browse for original game directory."""
        folder = QFileDialog.getExistingDirectory(
            self, 
            "Select Original Game Folder",
            str(Path.home()),
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        
        if folder:
            self.original_game_dir = Path(folder)
            self._widgets['original_game_dir'].setText(str(self.original_game_dir))
            self._update_config_from_ui()
            self._save_config()
            self._log(f"<span style='color:cyan'>Selected original game directory: {self.original_game_dir}</span>")

    def _open_original_game_dir(self):
        """Open the original game directory in the file explorer."""
        if not self.original_game_dir or not self.original_game_dir.exists():
            QMessageBox.warning(self, "No Folder", "Please select an original game folder first.")
            return
        
        if sys.platform == "win32":
            os.startfile(str(self.original_game_dir))
        else:
            subprocess.run(["xdg-open", str(self.original_game_dir)])

    def _browse_icon(self):
        """Browse for icon file."""
        if not self.project_root:
            QMessageBox.warning(self, "No Project", "Please select a project folder first.")
            return
        
        icon_file, _ = QFileDialog.getOpenFileName(
            self, "Select Icon File", str(self.project_root),
            "Icon Files (*.ico *.png);;All Files (*)"
        )
        
        if icon_file:
            # Make path relative to project root if possible
            try:
                rel_path = Path(icon_file).relative_to(self.project_root)
                self._widgets['icon_path'].setText(str(rel_path))
            except ValueError:
                self._widgets['icon_path'].setText(icon_file)
            self._on_setting_changed()

    def _on_setting_changed(self):
        """Handle setting changes."""
        if self.project_root:
            self._update_config_from_ui()
            self._save_config()
            if 'original_game_dir' in self._widgets and self._widgets['original_game_dir'].text().strip():
                self.original_game_dir = Path(self._widgets['original_game_dir'].text().strip())
            if 'include_hidden_files' in self._widgets:
                self.include_hidden_files = self._widgets['include_hidden_files'].isChecked()
            self._check_project_setup()

    def _run_diagnosis(self):
        """Run AI-powered project diagnosis."""
        if not self.project_root:
            QMessageBox.warning(self, "No Project", "Please select a project folder first.")
            return
        
        if not self.original_game_dir or not self.original_game_dir.exists():
            QMessageBox.warning(self, "No Game Folder", "Please select an original game folder first.")
            return
        
        model = self.cmb_model.currentText()
        if not model:
            QMessageBox.warning(self, "No Model", "Please select an AI model first.")
            return
        
        # Check if Ollama server is running
        try:
            subprocess.run(["ollama", "ps"], capture_output=True, text=True, check=True, timeout=5)
            self._log("<span style='color:cyan'>Ollama server is running</span>")
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            self._log("<span style='color:orange'>Ollama server not running. Starting server...</span>")
            try:
                subprocess.Popen(["ollama", "serve"], shell=True, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
                import time
                time.sleep(2)  # Give server time to start
                self._log("<span style='color:cyan'>Ollama server started</span>")
            except Exception as e:
                self._log(f"<span style='color:red'>Failed to start Ollama server: {str(e)}</span>")
                QMessageBox.critical(self, "Ollama Error", "Ollama server could not be started. Please ensure Ollama is installed and try again.")
                return
        
        self._log(f"<span style='color:cyan'>Starting diagnosis with model: {model}</span>")
        self._log(f"<span style='color:cyan'>Scanning directory: {self.clone_dir if self.clone_dir and self.clone_dir.exists() else self.original_game_dir}</span>")
        self.pb_diag.setValue(0)
        
        # Create and start thread
        self.diag_thread = QThread()
        self.diag_worker = Worker(self._diagnosis_worker, self.clone_dir if self.clone_dir and self.clone_dir.exists() else self.original_game_dir, model)
        self.diag_worker.moveToThread(self.diag_thread)
        self.diag_worker.log.connect(self._log)
        self.diag_worker.prog.connect(self.pb_diag.setValue)
        self.diag_worker.done.connect(lambda: self._log("<span style='color:lightgreen'>Diagnosis complete</span>"))
        self.diag_worker.done.connect(self.diag_thread.quit)
        self.diag_worker.done.connect(self.diag_worker.deleteLater)
        self.diag_thread.finished.connect(self.diag_thread.deleteLater)
        self.diag_worker.err.connect(self._show_error)
        self.diag_thread.started.connect(self.diag_worker.run)
        self.diag_thread.start()

    def _diagnosis_worker(self, worker, project_root, model):
        """Background diagnosis worker with snapshot generation and AI analysis."""
        project_root = Path(project_root)
        worker.log.emit(f"<span style='color:cyan'>Analyzing directory: {project_root}</span>")
        
        # Run static analysis
        worker.log.emit("<span style='color:cyan'>Running static analysis...</span>")
        try:
            results, scene_modules = audit_project(project_root)
            worker.prog.emit(20)
            
            # Format static results
            audit_info = "\n".join([f"{level}: {msg}" for level, msg in results])
            for level, message in results:
                color = {"INFO": "lightgreen", "WARNING": "orange", "ERROR": "red"}[level]
                worker.log.emit(f"<span style='color:{color}'>[{level}]</span> {message}")
        except Exception as e:
            worker.log.emit(f"<span style='color:red'>Static analysis failed: {str(e)}</span>")
            worker.err.emit(str(e))
            return
        
        # Generate project snapshot
        worker.log.emit("<span style='color:cyan'>Generating project snapshot...</span>")
        try:
            snapshot = generate_project_snapshot(project_root, include_hidden=self.include_hidden_files)
            # Extract summary from snapshot for logging
            summary_line = snapshot.splitlines()[-1] if snapshot else ""
            if summary_line.startswith("Summary:"):
                worker.log.emit(f"<span style='color:cyan'>Snapshot complete: {summary_line}</span>")
            else:
                worker.log.emit("<span style='color:cyan'>Snapshot complete</span>")
            worker.prog.emit(50)
        except Exception as e:
            worker.log.emit(f"<span style='color:red'>Snapshot generation failed: {str(e)}</span>")
            worker.err.emit(str(e))
            # Fallback to static results
            worker.prog.emit(100)
            return
        
        worker.prog.emit(60)
        
        # Try AI analysis with snapshot
        worker.log.emit(f"<span style='color:cyan'>Running AI model {model}...</span>")
        try:
            # Load a prompt (use first available or default)
            prompt_files = list(self.prompts_dir.glob("*.txt"))
            if prompt_files:
                prompt_content = prompt_files[0].read_text(encoding='utf-8')
            else:
                # Default enhanced AI prompt
                prompt_content = """Analyze this Panda3D project for packaging issues:

1. Identify files, patterns, or configurations that may fail when packaging with PyInstaller or Nuitka for Panda3D.
2. Detect incompatible file types, OS-specific paths, or Python dependencies known to cause build issues.
3. Check for Steamworks SDK dependencies in the sdk/ folder and report relevant files or libraries for packaging.
4. Suggest specific fixes or changes to ensure a successful .exe build.

Project structure:
{project_structure}

Static audit results:
{audit_results}

Build configuration:
{build_config}

Provide detailed recommendations to resolve identified issues."""
            
            # Format prompt with snapshot and other details
            formatted_prompt = prompt_content.format(
                project_structure=snapshot,
                audit_results=audit_info,
                build_config=json.dumps(self.cfg, indent=2),
                project_config=json.dumps(self.cfg, indent=2)
            )
            
            # Run Ollama with CPU library and timeout
            env = os.environ.copy()
            env["OLLAMA_LLM_LIBRARY"] = "cpu_avx2"  # Force CPU to avoid GPU crashes
            process = subprocess.Popen(
                ["ollama", "run", model],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env
            )
            
            # Communicate with timeout
            try:
                ai_output, ai_error = process.communicate(formatted_prompt, timeout=300)  # 5-minute timeout
            except subprocess.TimeoutExpired:
                process.terminate()
                process.wait(timeout=5)
                worker.log.emit("<span style='color:orange'>AI analysis timed out after 5 minutes</span>")
                worker.log.emit("<span style='color:cyan'>Falling back to static audit results</span>")
                worker.prog.emit(100)
                return
            
            # Ensure process is terminated
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=5)
            
            if process.returncode == 0 and ai_output.strip():
                worker.log.emit("<span style='color:lightblue'>AI Analysis Results:</span>")
                worker.log.emit(f"<span style='color:lightblue'>{ai_output.strip()}</span>")
            else:
                worker.log.emit(f"<span style='color:orange'>AI analysis failed: {ai_error}</span>")
                worker.log.emit("<span style='color:cyan'>Falling back to static audit results</span>")
                
        except (subprocess.CalledProcessError, FileNotFoundError, Exception) as e:
            worker.log.emit(f"<span style='color:orange'>AI analysis unavailable: {str(e)}</span>")
            worker.log.emit("<span style='color:cyan'>Falling back to static audit results</span>")
        
        worker.prog.emit(100)
        worker.log.emit("<span style='color:lightgreen'>AI analysis completed</span>")

    def _get_project_structure_info(self, project_root):
        """Get formatted project structure information (legacy, retained for compatibility)."""
        structure_lines = []
        for root, dirs, files in os.walk(project_root):
            # Skip hidden and build directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'venv', 'build', 'dist']]
            
            level = root.replace(str(project_root), '').count(os.sep)
            indent = '  ' * level
            structure_lines.append(f"{indent}{os.path.basename(root)}/")
            
            sub_indent = '  ' * (level + 1)
            for file in files:
                if not file.startswith('.') and not file.endswith('.pyc'):
                    structure_lines.append(f"{sub_indent}{file}")
                    
            if len(structure_lines) > 50:  # Limit output
                structure_lines.append("  ... (truncated)")
                break
        
        return '\n'.join(structure_lines)

    def _build_tab_build(self):
        """Build the Build configuration tab."""
        tab = QWidget()
        self.tabs.addTab(tab, "Build")
        layout = QVBoxLayout(tab)

        # Build section
        build_group = QGroupBox("Build Configuration")
        self._tip(build_group, "Configure settings for building your game executable")
        build_layout = QVBoxLayout(build_group)
        
        # Build output path display
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Build Output:"))
        self.lbl_build_output = QLabel("No project selected")
        self._tip(self.lbl_build_output, "Static output directory where builds will be placed")
        self.lbl_build_output.setStyleSheet("color: #ccc; font-style: italic; padding: 4px; background: #333; border: 1px solid #555;")
        output_layout.addWidget(self.lbl_build_output, 1)
        build_layout.addLayout(output_layout)
        
        btn_build = QPushButton("Build Game")
        self._tip(btn_build, "Compile your Panda3D project into an executable package from the cloned game folder")
        btn_build.clicked.connect(self._build_game)
        build_layout.addWidget(btn_build)
        
        self.pb_build = QProgressBar()
        self._tip(self.pb_build, "Shows progress of the build process")
        build_layout.addWidget(self.pb_build)
        
        layout.addWidget(build_group)

        # Advanced build options
        advanced_group = QGroupBox("Advanced Build Options")
        self._tip(advanced_group, "Additional settings to customize the build process")
        advanced_form = QFormLayout(advanced_group)
        
        # Additional asset directories
        self.txt_extra_assets = QLineEdit()
        self._tip(self.txt_extra_assets, "Comma-separated list of additional asset directories to include in the build")
        self.txt_extra_assets.textChanged.connect(self._on_advanced_setting_changed)
        advanced_form.addRow("Extra Assets:", self.txt_extra_assets)
        
        # Modules to exclude
        self.txt_exclude_modules = QLineEdit()
        self._tip(self.txt_exclude_modules, "Comma-separated list of Python modules to exclude from the build")
        self.txt_exclude_modules.textChanged.connect(self._on_advanced_setting_changed)
        advanced_form.addRow("Exclude Modules:", self.txt_exclude_modules)
        
        layout.addWidget(advanced_group)

    def _on_advanced_setting_changed(self):
        """Handle advanced setting changes."""
        if not self.project_root:
            return
        
        # Update config with advanced settings
        if hasattr(self, 'txt_extra_assets'):
            self.cfg['extra_assets'] = [x.strip() for x in self.txt_extra_assets.text().split(',') if x.strip()]
        if hasattr(self, 'txt_exclude_modules'):
            self.cfg['exclude_modules'] = [x.strip() for x in self.txt_exclude_modules.text().split(',') if x.strip()]
        
        self._save_config()

    def _build_game(self):
        """Launch the build process."""
        if not self.project_root:
            QMessageBox.warning(self, "No Project", "Please select a project folder first.")
            return
        
        if not self.original_game_dir or not self.original_game_dir.exists():
            QMessageBox.warning(self, "No Game Folder", "Please select an original game folder first.")
            return
        
        # Check UPX if enabled
        if self.cfg.get('compress_upx'):
            try:
                subprocess.run(["upx", "--version"], check=True, capture_output=True)
            except:
                QMessageBox.warning(self, "UPX Missing", "UPX not found. Please install or disable compression.")
                return
        
        # Clone the original game directory
        if self.clone_dir.exists():
            shutil.rmtree(self.clone_dir)
        self._log("<span style='color:cyan'>Cloning original game directory...</span>")
        try:
            shutil.copytree(self.original_game_dir, self.clone_dir, ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '*.pyo'))
            self._log(f"<span style='color:lightgreen'>Cloned game to: {self.clone_dir}</span>")
        except Exception as e:
            QMessageBox.critical(self, "Clone Error", f"Failed to clone game directory: {str(e)}")
            return
        
        # Validate entry script exists after cloning
        entry_script = self.clone_dir / self.cfg.get('entry_script', 'main.py')
        if not entry_script.exists():
            QMessageBox.critical(self, "Entry Script Missing", 
                               f"Entry script '{entry_script.name}' not found in cloned game directory.")
            return
        
        self._update_config_from_ui()
        self._save_config()
        
        self._log("<span style='color:cyan'>Starting build process...</span>")
        self.pb_build.setValue(0)
        
        thread = QThread()
        worker = Worker(self._build_worker, self.clone_dir, self.cfg, self.build_output_dir)
        worker.log.connect(self._log)
        worker.prog.connect(self.pb_build.setValue)
        worker.done.connect(lambda: self._log("<span style='color:lightgreen'>Build complete!</span>"))
        worker.done.connect(lambda: self._refresh_trees())
        worker.done.connect(thread.quit)
        worker.err.connect(self._show_error)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        thread.start()

    def _build_worker(self, worker, project_root, config, output_dir):
        """Background build worker."""
        project_root = Path(project_root)
        output_dir = Path(output_dir)
        
        # Clean previous builds
        worker.log.emit("Cleaning previous builds...")
        shutil.rmtree(output_dir, ignore_errors=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Clean PyInstaller temp directories
        for temp_dir in ['build', 'dist']:
            temp_path = project_root / temp_dir
            if temp_path.exists():
                shutil.rmtree(temp_path, ignore_errors=True)
        
        worker.prog.emit(10)
        
        # Analyze project for hidden imports
        worker.log.emit("Analyzing project structure...")
        results, scene_modules = audit_project(project_root)
        
        # Build PyInstaller command
        game_name = config.get('game_name', project_root.name)
        entry_script = config.get('entry_script', 'main.py')
        
        cmd = [
            'pyinstaller',
            '--onefile',
            '--windowed',  # No console window
            '--name', game_name,
            str(project_root / entry_script)
        ]
        
        # Add hidden imports for scene modules
        for module in scene_modules:
            cmd.extend(['--hidden-import', module])
        
        # Add common Panda3D hidden imports
        panda_imports = [
            'panda3d.core',
            'panda3d.physics',
            'panda3d.direct',
            'direct.showbase.ShowBase',
            'direct.task.Task',
            'direct.gui.DirectGui'
        ]
        for imp in panda_imports:
            cmd.extend(['--hidden-import', imp])
        
        # Add data directories
        asset_dirs = ['assets', 'models', 'textures', 'sounds', 'music', 'shaders', 'fonts']
        for asset_dir in asset_dirs:
            asset_path = project_root / asset_dir
            if asset_path.exists():
                cmd.extend(['--add-data', f'{asset_path}{os.pathsep}{asset_dir}'])
        
        # Add extra assets from config
        for extra_asset in config.get('extra_assets', []):
            extra_path = project_root / extra_asset
            if extra_path.exists():
                cmd.extend(['--add-data', f'{extra_path}{os.pathsep}{extra_asset}'])
        
        # Add icon if specified
        icon_path = config.get('icon_path', '')
        if icon_path:
            full_icon_path = project_root / icon_path
            if full_icon_path.exists():
                cmd.extend(['--icon', str(full_icon_path)])
        
        # Exclude modules
        for exclude_module in config.get('exclude_modules', []):
            cmd.extend(['--exclude-module', exclude_module])
        
        # UPX compression
        if config.get('compress_upx', False):
            upx_dir = config.get('upx_path', '')
            if upx_dir:
                cmd.append(f"--upx-dir={upx_dir}")
        
        # Add Steamworks SDK
        sdk_redist = self.SDK_DIR / "redistributable_bin"
        if sdk_redist.exists():
            cmd.extend(['--add-data', f'{sdk_redist}{os.pathsep}steam_sdk'])
        
        worker.prog.emit(20)
        
        # Run PyInstaller
        worker.log.emit(f"Running PyInstaller: {' '.join(cmd)}")
        try:
            process = subprocess.Popen(
                cmd,
                cwd=project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                universal_newlines=True
            )
            
            for line in process.stdout:
                worker.log.emit(line.strip())
            
            process.wait()
            if process.returncode != 0:
                raise subprocess.CalledProcessError(process.returncode, cmd)
                
        except subprocess.CalledProcessError as e:
            raise Exception(f"PyInstaller failed with return code {e.returncode}")
        
        worker.prog.emit(70)
        
        # Move build output
        dist_dir = project_root / 'dist'
        exe_name = f"{game_name}.exe" if sys.platform == 'win32' else game_name
        exe_path = dist_dir / exe_name
        
        if not exe_path.exists():
            raise FileNotFoundError(f"Built executable not found: {exe_path}")
        
        # Copy executable to output directory
        output_exe = output_dir / exe_name
        shutil.copy2(exe_path, output_exe)
        worker.log.emit(f"Executable copied to: {output_exe}")
        
        # Copy Steamworks SDK files
        if sdk_redist.exists():
            steam_api_dll = sdk_redist / "steam_api.dll" if sys.platform == "win32" else sdk_redist / "linux64" / "libsteam_api.so"
            if steam_api_dll.exists():
                shutil.copy2(steam_api_dll, output_dir)
                worker.log.emit(f"Copied Steamworks SDK: {steam_api_dll}")
        
        # Copy additional files
        readme_content = f"""# {game_name}

Built with Enhanced Panda3D Game Packager

## System Requirements
- Windows 10/11 (64-bit)
- DirectX 11 compatible graphics card
- 4GB RAM minimum

## Installation
Simply run {exe_name} to start the game.

## Troubleshooting
If you encounter issues, please check:
1. Graphics drivers are up to date
2. Windows is fully updated
3. Antivirus is not blocking the executable
"""
        if config.get('do_zip', False):
            readme_content += "\n## ZIP Archive\nA ZIP archive of the build is available: {game_name}_build.zip"
        if config.get('create_iso', False):
            readme_content += "\n## ISO Image\nAn ISO image has been created for disc burning or virtual mounting: {game_name}.iso"
        
        (output_dir / "README.txt").write_text(readme_content)
        
        # Create legal directory
        legal_dir = output_dir / "Legal"
        legal_dir.mkdir(exist_ok=True)
        (legal_dir / "LICENSE.txt").write_text("Copyright notice and license information goes here.")
        (legal_dir / "THIRD_PARTY.txt").write_text("Third-party software acknowledgments go here.")
        
        worker.prog.emit(85)
        
        # Create ZIP if requested
        if config.get('do_zip', False):
            worker.log.emit("Creating ZIP archive...")
            zip_path = output_dir.parent / f"{game_name}_build.zip"
            shutil.make_archive(str(zip_path.with_suffix('')), 'zip', output_dir)
            worker.log.emit(f"ZIP created: {zip_path}")
        
        # Create ISO if requested
        if config['create_iso']:
            worker.log.emit("Creating ISO...")
            iso_path = output_dir.parent / f"{game_name}.iso"
            oscdimg = config['oscdimg_path']
            if not oscdimg or not Path(oscdimg).exists():
                worker.log.emit("<span style='color:red'>ERROR: oscdimg path not set or invalid</span>")
            else:
                iso_cmd = [oscdimg, "-m", "-o", "-u2", f"-l{config['iso_label']}", str(output_dir), str(iso_path)]
                try:
                    subprocess.check_call(iso_cmd)
                    worker.log.emit(f"ISO created at: {iso_path}")
                    # Copy ISO to build_output
                    shutil.copy2(iso_path, output_dir / iso_path.name)
                except Exception as e:
                    worker.log.emit(f"<span style='color:red'>ISO creation failed: {str(e)}</span>")
        
        # Cleanup temporary directories
        for temp_dir in ['build', 'dist']:
            temp_path = project_root / temp_dir
            if temp_path.exists():
                shutil.rmtree(temp_path, ignore_errors=True)
        
        worker.prog.emit(100)
        worker.log.emit(f"Build completed successfully! Output: {output_dir}")

    def _build_tab_prompts(self):
        """Build the Prompt Management tab."""
        tab = QWidget()
        self.tabs.addTab(tab, "Prompts")
        layout = QHBoxLayout(tab)
        
        # Left side - Prompt list
        left_panel = QGroupBox("Available Prompts")
        self._tip(left_panel, "List and manage AI prompt templates for analysis")
        left_layout = QVBoxLayout(left_panel)
        
        self.prompt_list = QListWidget()
        self._tip(self.prompt_list, "List of available AI prompts for project analysis")
        self.prompt_list.itemClicked.connect(self._load_prompt)
        left_layout.addWidget(self.prompt_list)
        
        # Prompt management buttons
        prompt_buttons = QHBoxLayout()
        
        btn_add_prompt = QPushButton("Add Prompt")
        self._tip(btn_add_prompt, "Create a new AI prompt template")
        btn_add_prompt.clicked.connect(self._add_prompt)
        prompt_buttons.addWidget(btn_add_prompt)
        
        btn_delete_prompt = QPushButton("Delete Prompt")
        self._tip(btn_delete_prompt, "Delete the selected prompt template")
        btn_delete_prompt.clicked.connect(self._delete_prompt)
        prompt_buttons.addWidget(btn_delete_prompt)
        
        left_layout.addLayout(prompt_buttons)
        layout.addWidget(left_panel, 1)
        
        # Right side - Prompt editor
        right_panel = QGroupBox("Prompt Editor")
        self._tip(right_panel, "Edit AI prompt templates for analysis")
        right_layout = QVBoxLayout(right_panel)
        
        # Prompt name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Prompt Name:"))
        self.prompt_name = QLineEdit()
        self._tip(self.prompt_name, "Name of the current prompt file")
        name_layout.addWidget(self.prompt_name)
        right_layout.addLayout(name_layout)
        
        # Prompt content editor
        self.prompt_editor = QTextEdit()
        self._tip(self.prompt_editor, "Edit the AI prompt template. Use {placeholders} for dynamic content.")
        self.prompt_editor.setFont(QFont("Consolas", 10))
        right_layout.addWidget(self.prompt_editor)
        
        # Save button
        btn_save_prompt = QPushButton("Save Prompt")
        self._tip(btn_save_prompt, "Save changes to the current prompt")
        btn_save_prompt.clicked.connect(self._save_prompt)
        right_layout.addWidget(btn_save_prompt)
        
        # Placeholder help
        help_text = QLabel("""
Available placeholders:
• {project_structure} - Project directory tree
• {audit_results} - Static analysis results  
• {build_config} - Build configuration
• {project_config} - Project settings
        """)
        self._tip(help_text, "List of placeholders you can use in prompt templates")
        help_text.setStyleSheet("color: #aaa; font-size: 10px; padding: 10px;")
        right_layout.addWidget(help_text)
        
        layout.addWidget(right_panel, 2)
        
        # Load initial prompt list
        self._refresh_prompt_list()

    def _refresh_prompt_list(self):
        """Refresh the list of available prompts."""
        self.prompt_list.clear()
        if self.prompts_dir.exists():
            for prompt_file in self.prompts_dir.glob("*.txt"):
                self.prompt_list.addItem(prompt_file.stem)

    def _load_prompt(self):
        """Load selected prompt into editor."""
        current_item = self.prompt_list.currentItem()
        if not current_item:
            return
        
        prompt_name = current_item.text()
        prompt_file = self.prompts_dir / f"{prompt_name}.txt"
        
        if prompt_file.exists():
            self.prompt_name.setText(prompt_name)
            self.prompt_editor.setPlainText(prompt_file.read_text(encoding='utf-8'))
            self._log(f"<span style='color:cyan'>Loaded prompt: {prompt_name}</span>")

    def _add_prompt(self):
        """Add a new prompt."""
        name, ok = QInputDialog.getText(self, "New Prompt", "Prompt Name:")
        if not (ok and name.strip()):
            return
        
        # Sanitize filename
        safe_name = "".join(c for c in name.strip() if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_')
        
        if not safe_name:
            QMessageBox.warning(self, "Invalid Name", "Please enter a valid prompt name.")
            return
        
        prompt_file = self.prompts_dir / f"{safe_name}.txt"
        if prompt_file.exists():
            QMessageBox.warning(self, "Exists", "A prompt with this name already exists.")
            return
        
        # Fix: Use a default template content
        template_content = """Analyze this project:
{project_structure}"""
        prompt_file.write_text(template_content, encoding='utf-8')
        self._refresh_prompt_list()
        
        # Select the new prompt
        items = self.prompt_list.findItems(safe_name, Qt.MatchExactly)
        if items:
            self.prompt_list.setCurrentItem(items[0])
            self._load_prompt()
        
        self._log(f"<span style='color:lightgreen'>Created new prompt: {safe_name}</span>")

    def _delete_prompt(self):
        """Delete selected prompt."""
        current_item = self.prompt_list.currentItem()
        if not current_item:
            QMessageBox.information(self, "No Selection", "Please select a prompt to delete.")
            return
        
        prompt_name = current_item.text()
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete the prompt '{prompt_name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            prompt_file = self.prompts_dir / f"{prompt_name}.txt"
            if prompt_file.exists():
                prompt_file.unlink()
                self._refresh_prompt_list()
                self.prompt_name.clear()
                self.prompt_editor.clear()
                self._log(f"<span style='color:orange'>Deleted prompt: {prompt_name}</span>")

    def _save_prompt(self):
        """Save current prompt content."""
        if not self.prompt_name.text().strip():
            QMessageBox.warning(self, "No Name", "Please enter a prompt name.")
            return
        
        prompt_name = self.prompt_name.text().strip()
        prompt_file = self.prompts_dir / f"{prompt_name}.txt"
        
        try:
            prompt_file.write_text(self.prompt_editor.toPlainText(), encoding='utf-8')
            self._refresh_prompt_list()
            self._log(f"<span style='color:lightgreen'>Saved prompt: {prompt_name}</span>")
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save prompt: {str(e)}")

    def _build_tab_upload(self):
        """Build the Steam Upload tab."""
        tab = QWidget()
        self.tabs.addTab(tab, "Steam Upload")
        layout = QVBoxLayout(tab)

        # Steam configuration
        steam_group = QGroupBox("Steam Configuration")
        self._tip(steam_group, "Configure Steamworks settings for uploading your game")
        steam_form = QFormLayout(steam_group)
        
        # Steam App ID
        self.steam_appid = QLineEdit()
        self._tip(self.steam_appid, "Your Steam Application ID from Steamworks (find in Steamworks Partner Portal)")
        self.steam_appid.textChanged.connect(self._on_steam_setting_changed)
        steam_form.addRow("Steam App ID:", self.steam_appid)
        
        # Steam Depot ID
        self.steam_depot_id = QLineEdit()
        self._tip(self.steam_depot_id, "Steam Depot ID for your game content (configured in Steamworks)")
        self.steam_depot_id.textChanged.connect(self._on_steam_setting_changed)
        steam_form.addRow("Depot ID:", self.steam_depot_id)
        
        # Steam Username
        self.steam_username = QLineEdit()
        self._tip(self.steam_username, "Your Steam username for authenticated uploads")
        self.steam_username.textChanged.connect(self._on_steam_setting_changed)
        steam_form.addRow("Steam Username:", self.steam_username)
        
        # ContentBuilder path
        cb_layout = QHBoxLayout()
        self.steam_cb_path = QLineEdit()
        self._tip(self.steam_cb_path, 
                 """Path to Steam ContentBuilder directory (contains steamcmd.exe and scripts folder).
                    Found in sdk/tools/ContentBuilder in the Steamworks SDK.
                    Used to upload your game to Steam via SteamCmd.""")
        cb_browse = QPushButton("Browse")
        self._tip(cb_browse, "Select the Steam ContentBuilder directory")
        cb_browse.clicked.connect(self._browse_contentbuilder)
        cb_layout.addWidget(self.steam_cb_path)
        cb_layout.addWidget(cb_browse)
        steam_form.addRow("ContentBuilder Path:", cb_layout)
        
        # Validate Steam Config button
        btn_validate_steam = QPushButton("Validate Steam Config")
        self._tip(btn_validate_steam, "Check if Steam configuration and ContentBuilder path are valid")
        btn_validate_steam.clicked.connect(self._validate_steam_config)
        steam_form.addRow("", btn_validate_steam)
        
        layout.addWidget(steam_group)
        
        # Upload section
        upload_group = QGroupBox("Upload to Steam")
        self._tip(upload_group, "Tools to upload your built game to Steam")
        upload_layout = QVBoxLayout(upload_group)
        
        # Upload prerequisites
        prereq_label = QLabel("Steam Upload Prerequisites:")
        self._tip(prereq_label, "Checklist of requirements for a successful Steam upload")
        upload_layout.addWidget(prereq_label)
        
        prereq_text = QTextBrowser()
        self._tip(prereq_text, "Steps and requirements for uploading to Steam")
        prereq_text.setHtml("""
            <p><b>Before uploading, ensure:</b></p>
            <ul>
                <li>Steam App ID is valid and you have access in Steamworks</li>
                <li>Depot ID is configured in Steamworks for your app</li>
                <li>Steam username has access to the App ID</li>
                <li>ContentBuilder directory contains steamcmd.exe and scripts folder</li>
                <li>Steamworks SDK is present in sdk/ folder</li>
                <li>Game has been built successfully (check Build tab)</li>
                <li>Steam Guard is disabled or configured for automated login</li>
            </ul>
        """)
        prereq_text.setMaximumHeight(150)
        upload_layout.addWidget(prereq_text)
        
        btn_upload = QPushButton("Upload to Steam")
        self._tip(btn_upload, "Upload the built game to Steam using ContentBuilder and SteamCmd")
        btn_upload.clicked.connect(self._upload_to_steam)
        upload_layout.addWidget(btn_upload)
        
        self.pb_upload = QProgressBar()
        self._tip(self.pb_upload, "Shows progress of the Steam upload process")
        upload_layout.addWidget(self.pb_upload)
        
        layout.addWidget(upload_group)

    def _on_steam_setting_changed(self):
        """Handle Steam setting changes."""
        if not self.project_root:
            return
        
        self.cfg['steam_appid'] = self.steam_appid.text().strip()
        self.cfg['steam_depot_id'] = self.steam_depot_id.text().strip()
        self.cfg['steam_username'] = self.steam_username.text().strip()
        self.cfg['cb_path'] = self.steam_cb_path.text().strip()
        self._save_config()

    def _browse_contentbuilder(self):
        """Browse for ContentBuilder directory."""
        default_dir = str(self.SDK_DIR / "tools" / "ContentBuilder") if (self.SDK_DIR / "tools" / "ContentBuilder").exists() else str(Path.home())
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Steam ContentBuilder Directory",
            default_dir,
            QFileDialog.ShowDirsOnly
        )
        
        if folder:
            self.steam_cb_path.setText(folder)

    def _validate_steam_config(self):
        """Validate Steam configuration."""
        errors = []
        
        if not self.steam_appid.text().strip():
            errors.append("Steam App ID is required")
        if not self.steam_depot_id.text().strip():
            errors.append("Steam Depot ID is required")
        if not self.steam_username.text().strip():
            errors.append("Steam Username is required")
        
        cb_path = Path(self.steam_cb_path.text().strip()) if self.steam_cb_path.text().strip() else None
        if not cb_path or not cb_path.exists():
            errors.append("ContentBuilder path is invalid or not set")
        elif not (cb_path / "builder" / "steamcmd.exe").exists() and not (cb_path / "steamcmd.exe").exists():
            errors.append("steamcmd.exe not found in ContentBuilder directory")
        
        if not self.SDK_DIR.exists():
            errors.append("Steamworks SDK not found in sdk/ folder")
        
        if errors:
            QMessageBox.warning(self, "Validation Failed", "Please fix the following issues:\n" + "\n".join(errors))
        else:
            QMessageBox.information(self, "Validation Success", "Steam configuration appears valid!")
            self._log("<span style='color:lightgreen'>Steam configuration validated successfully</span>")

    def _upload_to_steam(self):
        """Upload build to Steam."""
        if not self.project_root or not self.build_output_dir:
            QMessageBox.warning(self, "No Project", "Please select a project and build it first.")
            return
        
        if not self.build_output_dir.exists() or not any(self.build_output_dir.iterdir()):
            QMessageBox.warning(self, "No Build", "Please build the project first.")
            return
        
        # Validate Steam settings
        if not all([self.steam_appid.text().strip(), self.steam_depot_id.text().strip(), self.steam_username.text().strip(), self.steam_cb_path.text().strip()]):
            QMessageBox.warning(self, "Missing Settings", "Please fill in all Steam configuration fields.")
            return
        
        self._log("<span style='color:cyan'>Starting Steam upload...</span>")
        self.pb_upload.setValue(0)
        
        thread = QThread()
        worker = Worker(self._upload_worker, self.build_output_dir, self.cfg)
        worker.log.connect(self._log)
        worker.prog.connect(self.pb_upload.setValue)
        worker.done.connect(lambda: self._log("<span style='color:lightgreen'>Steam upload complete!</span>"))
        worker.done.connect(thread.quit)
        worker.err.connect(self._show_error)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        thread.start()

    def _upload_worker(self, worker, build_dir, config):
        """Background Steam upload worker."""
        build_dir = Path(build_dir)
        cb_path = Path(config['cb_path'])
        
        # Validate ContentBuilder path
        if not cb_path.exists():
            raise FileNotFoundError(f"ContentBuilder path not found: {cb_path}")
        
        steamcmd_exe = cb_path / "builder" / "steamcmd.exe"
        if not steamcmd_exe.exists():
            steamcmd_exe = cb_path / "steamcmd.exe"  # Alternative location
        
        if not steamcmd_exe.exists():
            raise FileNotFoundError("steamcmd.exe not found in ContentBuilder directory")
        
        worker.prog.emit(10)
        
        # Copy build content to ContentBuilder
        worker.log.emit("Copying build content to ContentBuilder...")
        content_dir = cb_path / "content"
        if content_dir.exists():
            shutil.rmtree(content_dir)
        shutil.copytree(build_dir, content_dir)
        
        # Copy Steamworks SDK files
        sdk_redist = self.SDK_DIR / "redistributable_bin"
        if sdk_redist.exists():
            steam_api_dll = sdk_redist / "steam_api.dll" if sys.platform == "win32" else sdk_redist / "linux64" / "libsteam_api.so"
            if steam_api_dll.exists():
                shutil.copy2(steam_api_dll, content_dir)
                worker.log.emit(f"Copied Steamworks SDK: {steam_api_dll}")
        
        worker.prog.emit(30)
        
        # Generate VDF script
        worker.log.emit("Generating Steam VDF script...")
        scripts_dir = cb_path / "scripts"
        scripts_dir.mkdir(exist_ok=True)
        
        app_id = config['steam_appid']
        depot_id = config['steam_depot_id']
        vdf_path = scripts_dir / f"app_build_{app_id}.vdf"
        
        vdf_content = f'''\
"AppBuild"
{{
    "AppID" "{app_id}"
    "Desc" "Build from Enhanced Panda3D Packager"
    "ContentRoot" "{content_dir.as_posix()}"
    "BuildOutput" "{(cb_path / 'output').as_posix()}"
    "Depots"
    {{
        "{depot_id}"
        {{
            "FileMapping"
            {{
                "LocalPath" "*"
                "DepotPath" "."
                "recursive" "1"
            }}
        }}
    }}
}}
'''
        
        vdf_path.write_text(vdf_content.strip())
        worker.log.emit(f"VDF script created: {vdf_path}")
        
        worker.prog.emit(50)
        
        # Run SteamCmd
        worker.log.emit("Running SteamCmd upload...")
        cmd = [
            str(steamcmd_exe),
            "+login", config['steam_username'],
            "+run_app_build", str(vdf_path),
            "+quit"
        ]
        
        try:
            process = subprocess.Popen(
                cmd,
                cwd=cb_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                universal_newlines=True
            )
            
            for line in process.stdout:
                worker.log.emit(line.strip())
                
            process.wait()
            if process.returncode != 0:
                raise subprocess.CalledProcessError(process.returncode, cmd)
                
        except subprocess.CalledProcessError as e:
            raise Exception(f"SteamCmd failed with return code {e.returncode}")
        
        worker.prog.emit(100)
        worker.log.emit("Steam upload completed successfully!")

    def _refresh_trees(self):
        """Refresh both file trees."""
        # Project tree
        if self.project_root:
            self.tree_proj.model.setRootPath(str(self.project_root))
            self.tree_proj.tree.setRootIndex(self.tree_proj.model.index(str(self.project_root)))
        
        # Build tree
        if self.build_output_dir and self.build_output_dir.exists():
            self.tree_build.model.setRootPath(str(self.build_output_dir))
            self.tree_build.tree.setRootIndex(self.tree_build.model.index(str(self.build_output_dir)))
            self.lbl_build_output.setText(str(self.build_output_dir))
            self.lbl_build_output.setStyleSheet("color: #00cc66; font-weight: bold; padding: 4px; background: #333; border: 1px solid #555;")

    def _log(self, message):
        """Add message to console with auto-scroll."""
        self.console.append(message)
        scrollbar = self.console.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _show_error(self, error_text):
        """Show detailed error dialog."""
        dialog = QMessageBox(self)
        dialog.setIcon(QMessageBox.Critical)
        dialog.setWindowTitle("Error")
        dialog.setText("An error occurred during operation:")
        
        # Create expandable details
        details = QTextEdit()
        details.setPlainText(error_text)
        details.setReadOnly(True)
        dialog.layout().addWidget(details)
        dialog.setDetailedText(error_text)  # Fallback for older PyQt
        
        dialog.exec_()

# ─────────────────────────────────────────────────────────────────────────────
def exception_handler(type, value, tb):
    """Global exception handler to show popup with error."""
    error_text = "".join(traceback.format_exception(type, value, tb))
    dialog = QMessageBox()
    dialog.setIcon(QMessageBox.Critical)
    dialog.setWindowTitle("Fatal Error")
    dialog.setText("An unhandled exception occurred:")
    
    details = QTextEdit()
    details.setPlainText(error_text)
    details.setReadOnly(True)
    dialog.layout().addWidget(details)
    dialog.setDetailedText(error_text)
    
    dialog.exec_()
    sys.exit(1)

sys.excepthook = exception_handler

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
```

Enhanced Panda3D packager / auditor / Steam uploader GUI.

New Features:
• Project folder selection with dropdown menu from C:\\Users\\Art PC\\Desktop\\Custom_Compiler\\Projects
• Original game folder input with cloning to prevent tampering
• Enhanced tooltips for all settings with 3-second delay
• Prompt management system with Ollama integration
• Default prompt templates auto-creation
• Improved project structure display
• Enhanced Steam configuration with username and validation
• Integration with Steamworks SDK in sdk/ folder
• Full project snapshot generation with AI-powered analysis
• ISO generation
• oscdimg/mkisofs support
• Icon converter launcher
• UPX-path override
**Classes:** SlowTipStyle, Worker, MainWindow
**Functions:** create_default_prompts(prompts_dir), audit_project(project_dir), generate_project_snapshot(root_path, include_hidden), exception_handler(type, value, tb)


## Module `panel_creator.py`

```python
#!/usr/bin/env python3
"""
tests/panel_creator.py

A quick PyQt5‑based Panel/Scene Generator for Rats n Goblins (now in tests/):
• Enter a panel/scene name (CamelCase)
• Select target folder or script via a scrollable tree view of the entire project
• Choose to generate a Python panel script (launches it briefly to auto‑generate SB)
  or an SB template for an existing script
• “Generate” writes the file(s) and logs their paths + contents in the Output Log
• “Delete” removes the selected file (with confirmation)
• “Ctrl+Z” undoes the last deletion
• “Copy Log” copies the entire Output Log to clipboard
• “Refresh” clears inputs and the Output Log for the next session
"""

import os
import sys
import subprocess
import threading
from pathlib import Path

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QLabel, QLineEdit, QPushButton, QRadioButton,
    QButtonGroup, QTextEdit, QVBoxLayout, QHBoxLayout,
    QMessageBox, QFileSystemModel, QTreeView, QShortcut
)
from PyQt5.QtCore import QDir
from PyQt5.QtGui import QClipboard, QKeySequence

# PROJECT_ROOT is now one level up from tests/
PROJECT_ROOT  = Path(__file__).parent.parent.resolve()
TEMPLATE_FILE = PROJECT_ROOT / "panel_template.py"

class PanelCreator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Panel / Scene Generator")
        self.setFixedSize(700, 550)

        # Track selection (folder or file) in the tree
        self.selected_path = str(PROJECT_ROOT)
        # Stack for undoing deletions: list of (Path, bytes)
        self.undo_stack = []

        # Widgets
        self.name_input    = QLineEdit()
        self.python_radio  = QRadioButton("Python Panel")
        self.sb_radio      = QRadioButton("SB Template")
        self.generate_btn  = QPushButton("Generate")
        self.delete_btn    = QPushButton("Delete")
        self.refresh_btn   = QPushButton("Refresh")
        self.copy_btn      = QPushButton("Copy Log")
        self.output_log    = QTextEdit()
        self.output_log.setReadOnly(True)

        # File tree model & view rooted at the actual project root
        self.model = QFileSystemModel()
        self.model.setRootPath(str(PROJECT_ROOT))
        self.model.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs | QDir.Files)
        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(str(PROJECT_ROOT)))
        # Hide all columns except the name
        for col in range(1, self.model.columnCount()):
            self.tree.hideColumn(col)
        self.tree.clicked.connect(self.on_tree_clicked)

        # Radio group for file type
        self.radio_group = QButtonGroup()
        self.radio_group.addButton(self.python_radio)
        self.radio_group.addButton(self.sb_radio)
        self.python_radio.setChecked(True)

        # Layout setup
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        layout.addWidget(QLabel("Panel/Scene Name (CamelCase):"))
        layout.addWidget(self.name_input)

        layout.addWidget(QLabel("Select Folder or Script:"))
        layout.addWidget(self.tree, stretch=2)

        layout.addWidget(QLabel("File Type:"))
        type_row = QHBoxLayout()
        type_row.addWidget(self.python_radio)
        type_row.addWidget(self.sb_radio)
        layout.addLayout(type_row)

        btn_row = QHBoxLayout()
        btn_row.addWidget(self.generate_btn)
        btn_row.addWidget(self.delete_btn)
        btn_row.addWidget(self.refresh_btn)
        btn_row.addWidget(self.copy_btn)
        layout.addLayout(btn_row)

        layout.addWidget(QLabel("Output Log:"))
        layout.addWidget(self.output_log, stretch=1)

        # Connect signals
        self.generate_btn.clicked.connect(self.generate)
        self.delete_btn.clicked.connect(self.delete_selected)
        self.refresh_btn.clicked.connect(self.refresh)
        self.copy_btn.clicked.connect(self.copy_log)

        # Undo shortcut (Ctrl+Z)
        undo_sc = QShortcut(QKeySequence("Ctrl+Z"), self)
        undo_sc.activated.connect(self.undo_delete)

        # Initialize state
        self.refresh()

    def on_tree_clicked(self, index):
        """Store the path of the clicked item."""
        self.selected_path = self.model.filePath(index)

    def generate(self):
        """Generate a Python panel or SB template based on the selection."""
        name      = self.name_input.text().strip()
        spath     = Path(self.selected_path)
        is_python = self.python_radio.isChecked()

        if not name:
            QMessageBox.critical(self, "Error", "Please enter a panel/scene name.")
            return

        created = []

        if is_python:
            # Determine target folder under the project
            folder = spath if spath.is_dir() else spath.parent
            target_py = folder / f"{name.lower()}.py"
            if target_py.exists():
                QMessageBox.critical(self, "Error", f"{target_py} already exists.")
                return
            if not TEMPLATE_FILE.exists():
                QMessageBox.critical(self, "Error", f"Template missing: {TEMPLATE_FILE}")
                return

            # Write the Python panel from the template
            content_py = TEMPLATE_FILE.read_text(encoding="utf-8").replace("{ClassName}", name)
            target_py.write_text(content_py, encoding="utf-8")
            created.append((target_py, content_py))

            # Launch the new panel briefly so it auto-generates its SB file
            try:
                proc = subprocess.Popen([sys.executable, str(target_py)])
                timer = threading.Timer(0.5, proc.terminate)
                timer.start()
                proc.wait()
                timer.cancel()
            except Exception as e:
                created.append((None, f"ERROR launching script: {e}"))

        else:
            # SB template for an existing .py panel
            if not spath.is_file() or spath.suffix.lower() != ".py":
                QMessageBox.critical(self, "Error", "Select a .py panel script for SB generation.")
                return
            sb_path = spath.with_suffix(".sb")
            if sb_path.exists():
                QMessageBox.critical(self, "Error", f"{sb_path} already exists.")
                return

            sb_content = (
                "# Scene Blueprint (SB) template\n"
                f"scene_name = \"{spath.stem.title()}\"\n\n"
                "# Define UI elements and actions here\n"
                "# Example:\n"
                "# Button(id=\"play\", label=\"Play\", pos=(0,0.2), size=(0.3,0.1))\n"
                "#     .action(load_scene, \"GameState\")\n"
            )
            sb_path.write_text(sb_content, encoding="utf-8")
            created.append((sb_path, sb_content))

        # Output created files and contents
        for path, content in created:
            if path:
                self._log(f"--- Created: {path} ---")
            self._log(content + "\n")

    def delete_selected(self):
        """Delete the selected file, with confirmation (no log entry)."""
        spath = Path(self.selected_path)
        if not spath.exists() or not spath.is_file():
            QMessageBox.critical(self, "Error", "Select a file to delete.")
            return
        reply = QMessageBox.question(
            self, "Confirm Delete", f"Delete {spath.name}?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        # Backup for undo
        content = spath.read_bytes()
        self.undo_stack.append((spath, content))

        try:
            spath.unlink()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Deletion failed: {e}")

    def undo_delete(self):
        """Restore the last deleted file from the undo stack (no log entry)."""
        if not self.undo_stack:
            QMessageBox.information(self, "Undo", "Nothing to undo.")
            return
        path, content = self.undo_stack.pop()
        try:
            path.write_bytes(content)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Restore failed: {e}")

    def refresh(self):
        """Reset inputs and clear the output log."""
        self.name_input.clear()
        self.python_radio.setChecked(True)
        self.output_log.clear()
        self.selected_path = str(PROJECT_ROOT)

    def copy_log(self):
        """Copy the entire output log contents to the clipboard."""
        clipboard: QClipboard = QApplication.clipboard()
        clipboard.setText(self.output_log.toPlainText())
        QMessageBox.information(self, "Copied", "Output Log copied to clipboard.")

    def _log(self, msg: str):
        """Append a line to the output log."""
        self.output_log.append(msg)

def main():
    app = QApplication(sys.argv)
    window = PanelCreator()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
```

tests/panel_creator.py

A quick PyQt5‑based Panel/Scene Generator for Rats n Goblins (now in tests/):
• Enter a panel/scene name (CamelCase)
• Select target folder or script via a scrollable tree view of the entire project
• Choose to generate a Python panel script (launches it briefly to auto‑generate SB)
  or an SB template for an existing script
• “Generate” writes the file(s) and logs their paths + contents in the Output Log
• “Delete” removes the selected file (with confirmation)
• “Ctrl+Z” undoes the last deletion
• “Copy Log” copies the entire Output Log to clipboard
• “Refresh” clears inputs and the Output Log for the next session
**Classes:** PanelCreator
**Functions:** main()


## Module `Simple_Packager.py`

```python
#!/usr/bin/env python3
# interactive_packager.py — GUI packager & “self‑healing” retry engine for Panda3D

"""
This script provides a GUI front‑end for packaging Panda3D games into
self‑contained executables.  It clones a project into a temporary
directory, invokes PyInstaller to build a one‑file binary and then
optionally retries with user‑supplied fixes if the build fails.  The
script has been enhanced to better handle Panda3D projects: it will
automatically discover a project‑local virtual environment, include
data directories (e.g. models or textures) via PyInstaller's
``--add-data`` option and collect all resources from the ``panda3d``
package.
"""

import sys
import os
import shutil
import subprocess
import tempfile
import traceback
import json
import ctypes
import re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from PyQt5.QtCore import Qt, QObject, pyqtSignal, QThread, qInstallMessageHandler, QtMsgType
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QFileDialog, QTextEdit,
    QTreeView, QFileSystemModel, QHeaderView, QProgressBar,
    QProxyStyle, QStyle, QToolTip, QMessageBox, QInputDialog, QDialog,
    QPlainTextEdit, QGroupBox, QDialogButtonBox, QComboBox
)

# ─────────────────────────────────────────────────────────────────────
# Suppress Windows crash dialogs
if sys.platform == "win32":
    SEM_FAILCRITICALERRORS = 0x0001
    SEM_NOGPFAULTERRORBOX = 0x0002
    ctypes.windll.kernel32.SetErrorMode(SEM_FAILCRITICALERRORS | SEM_NOGPFAULTERRORBOX)


def qt_message_handler(msg_type, ctx, msg):
    """Redirect Qt fatal messages to a message box."""
    if msg_type in (QtMsgType.QtCriticalMsg, QtMsgType.QtFatalMsg):
        QMessageBox.critical(None, "Qt Fatal", msg)


qInstallMessageHandler(qt_message_handler)


class SlowTipStyle(QProxyStyle):
    """Custom Qt style that delays tooltips so they don't appear instantly."""
    def styleHint(self, hint, opt, w, ret):
        if hint == QStyle.SH_ToolTip_WakeUpDelay:
            return 3000
        return super().styleHint(hint, opt, w, ret)


# ─────────────────────────────────────────────────────────────────────
# Error→fix rules for parsing build logs
RULES = [
    {
        "pattern": r"No graphics pipe is available",
        "prompt": "No display driver found. Choose one:",
        "choices": ["pandagl", "p3tinydisplay"],
        "action": "load_display",
    },
    {
        "pattern": r"Missing module '(.+?)'",
        "prompt": "Add hidden import for module '{0}'?",
        "action": "hidden_import",
    },
    {
        "pattern": r"Warning: no venv found",
        "prompt": "Select your venv folder now?",
        "action": "select_venv",
    },
    {
        "pattern": r"No module named PyInstaller",
        "prompt": "PyInstaller is not installed in the selected Python environment. Would you like to install it now?",
        "action": "install_pyinstaller",
    },
]


# Log filenames
ACTIVITY_LOG = "activity.log"
BUILD_LOG = "build.log"
TEST_LOG = "test_launch.log"
PRACTICES = "Panda3D_packaging_practices.txt"
USER_CFG = "user_config.json"


def clean_clone(src: Path, dst: Path, log_fn=None):
    """Recursively copy a project to a new location, skipping venvs and caches.

    Files are copied using a ThreadPoolExecutor for improved performance.
    """
    files = []
    for root, dirs, fs in os.walk(src):
        dirs[:] = [d for d in dirs if d not in ("venv", "__pycache__")]
        rel = Path(root).relative_to(src)
        tgt = dst / rel
        tgt.mkdir(parents=True, exist_ok=True)
        for f in fs:
            if f.endswith((".pyc", ".pyo")):
                continue
            files.append((Path(root) / f, tgt / f))
    workers = min(32, os.cpu_count() or 4)
    if log_fn:
        log_fn(f"📂 Copying {len(files)} files using {workers} threads…")
    with ThreadPoolExecutor(max_workers=workers) as exe:
        futures = {exe.submit(shutil.copy2, s, d): (s, d) for s, d in files}
        for fut in as_completed(futures):
            s, d = futures[fut]
            try:
                fut.result()
            except Exception as e:
                if log_fn:
                    log_fn(f"⚠️ Failed copy {s.name}: {e}")


# ─────────────────────────────────────────────────────────────────────
class BuildWindow(QDialog):
    """A window that streams PyInstaller output into a read‑only text box."""

    def __init__(self, cmd, cwd):
        super().__init__(None, Qt.WindowTitleHint | Qt.WindowSystemMenuHint)
        self.setWindowTitle("Build Output")
        self.resize(700, 500)

        v = QVBoxLayout(self)
        self.txt = QPlainTextEdit(readOnly=True)
        v.addWidget(self.txt, 1)
        btns = QDialogButtonBox(QDialogButtonBox.Close)
        btns.rejected.connect(self.reject)
        v.addWidget(btns)

        # Start subprocess and immediately begin reading its output
        self.proc = subprocess.Popen(
            cmd,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        self._read_loop()

    def _read_loop(self):
        for line in self.proc.stdout:
            # Append build output to the widget and write to build.log
            self.txt.appendPlainText(line.rstrip())
            # Write using UTF‑8 with ignore to avoid encoding errors on Windows
            with open(BUILD_LOG, "a", encoding="utf-8", errors="ignore") as f:
                f.write(line)
        self.proc.wait()
        self.txt.appendPlainText(f"\n🏁 Build exited code {self.proc.returncode}")


# ─────────────────────────────────────────────────────────────────────
class Worker(QObject):
    """Performs the build process in a separate thread and emits progress.

    A Worker instance clones the project, constructs a PyInstaller command,
    runs the build and optionally retries with fixes if the build fails.
    """

    activity = pyqtSignal(str)
    prog = pyqtSignal(int)
    done = pyqtSignal()
    err = pyqtSignal(str)

    def __init__(self, cfg):
        super().__init__()
        self.cfg = cfg
        self.inbound = Path(cfg["project_folder"])
        self.iso_folder = Path(cfg["iso_folder"]) if cfg["iso_folder"] else None
        self.entry = cfg.get("entry_script") or "main.py"
        self.exe_name = cfg.get("exe_name") or self.inbound.name
        # Always save builds under the script's own Builds folder.  Use
        # the directory where this module resides to compute an
        # absolute path so that builds land in Custom_Compiler/Builds
        # regardless of the current working directory.
        self.output_dir = Path(__file__).parent / "Builds" / self.exe_name
        self.hidden_imports = []
        self.display_driver = None
        self.retries = 3

        # Determine which Python interpreter to use for building.  If the
        # configuration specifies one, honour it.  Otherwise attempt to
        # discover a Python executable from a local virtual environment
        # within the project folder.  If no venv can be found, fall
        # back to the current interpreter.
        venv_py_cfg = cfg.get("venv_python")
        if venv_py_cfg:
            self.venv_python = venv_py_cfg
        else:
            cand_win = self.inbound / "venv" / "Scripts" / "python.exe"
            cand_unx = self.inbound / "venv" / "bin" / "python"
            if cand_win.exists():
                self.venv_python = str(cand_win)
                self.log(f"🐍 Using project venv python → {cand_win}")
            elif cand_unx.exists():
                self.venv_python = str(cand_unx)
                self.log(f"🐍 Using project venv python → {cand_unx}")
            else:
                self.venv_python = sys.executable
                self.log(f"🐍 No project venv found; falling back to {sys.executable}")

    def log(self, msg: str) -> None:
        """Emit a message to the activity feed and append to the log file.

        The log file is opened with UTF‑8 encoding and characters that
        cannot be encoded in the system default (such as emoji) are
        ignored to prevent UnicodeEncodeError on Windows (cp1252).
        """
        self.activity.emit(msg)
        try:
            with open(ACTIVITY_LOG, "a", encoding="utf-8", errors="ignore") as f:
                f.write(msg + "\n")
        except Exception:
            # Fallback if the log cannot be written for some reason
            pass

    def run(self) -> None:
        """Entry point for the worker thread.  Executes the build with retries."""
        try:
            # Clear previous logs
            open(ACTIVITY_LOG, "w").close()
            open(BUILD_LOG, "w").close()
            for attempt in range(1, self.retries + 1):
                self.log(f"🔄 Build attempt {attempt}/{self.retries}")
                if self._build_once():
                    self.done.emit()
                    return
                self.log("🔁 Retrying with applied fixes…")
            raise RuntimeError("❌ Build failed after multiple attempts")
        except Exception:
            self.err.emit(traceback.format_exc())

    def _build_once(self) -> bool:
        """Perform a single build attempt.

        Returns True on success or False if fixes were applied and a retry
        should occur.
        """
        # Construct the base PyInstaller command
        cmd = [
            self.venv_python,
            "-m",
            "PyInstaller",
            "--noconfirm",
            "--onefile",
            "--windowed",
            "--name",
            self.exe_name,
        ]
        # Optionally force a Panda3D display driver
        if self.display_driver:
            from panda3d.core import loadPrcFileData
            loadPrcFileData("", f"load-display {self.display_driver}")

        # Append hidden imports accumulated from previous runs
        for hi in self.hidden_imports:
            cmd.append(f"--hidden-import={hi}")

        self.log("🏗️ Preparing clone…")
        with tempfile.TemporaryDirectory(prefix="p3build_") as tmp:
            bd = Path(tmp) / "clone"
            clean_clone(self.inbound, bd, log_fn=self.log)
            self.prog.emit(20)

            ep = bd / self.entry
            if not ep.exists():
                QMessageBox.warning(None, "Entry Missing", f"Cannot find {self.entry}.")
                return False

            # Detect resource directories and add them to the PyInstaller command.
            data_dirs = []
            for name in ("models", "assets", "resources", "textures", "data"):
                p = bd / name
                if p.exists() and p.is_dir():
                    data_dirs.append(p)
            # Always collect all Panda3D data (models, shaders, etc.)
            cmd += ["--collect-all", "panda3d"]
            # Add discovered data directories
            for d in data_dirs:
                dest = d.relative_to(bd)
                sep = ';' if os.name == 'nt' else ':'
                cmd += ["--add-data", f"{d}{sep}{dest}"]
                self.log(f"📦 Added data directory: {dest}")

            # -----------------------------------------------------------------
            # Include all Python packages in the project
            #
            # PyInstaller determines which modules to include by tracing import
            # statements at build time.  However, games like Rats N Goblins
            # frequently load scenes or components dynamically using
            # importlib.import_module or by constructing module names from
            # strings.  These dynamic imports are invisible to PyInstaller's
            # analysis and therefore the associated modules are omitted from
            # the packaged executable.  When such a module is missing at
            # runtime, the game may emit errors like “Scene 'MainMenu' not
            # found” even though the file exists in the source tree.  To
            # mitigate this, we proactively collect every package (i.e.
            # directories containing an __init__.py) at the top level of the
            # cloned project and instruct PyInstaller to include all of
            # their submodules and data.  The --collect-all flag bundles
            # both Python code and package resources.  This ensures that
            # dynamically imported modules such as scenes.mainmenu are
            # available in the final executable without having to manually
            # specify hidden imports.
            pkg_dirs = []
            for child in bd.iterdir():
                try:
                    init_file = child / '__init__.py'
                except Exception:
                    continue
                if child.is_dir() and init_file.exists():
                    pkg_dirs.append(child)
            for pkg_dir in pkg_dirs:
                pkg_name = pkg_dir.name
                cmd += ["--collect-all", pkg_name]
                self.log(f"📦 Added Python package: {pkg_name} (collect all)")

            # Scan top-level directories in the cloned project for additional
            # resource directories (non-Python files).  These may include
            # things like schemas, api keys, assets or other data that
            # PyInstaller would not pick up automatically.  Only include
            # a directory if it contains at least one file whose name
            # does not end with .py or .pyc.
            for child in bd.iterdir():
                if child.is_dir() and child.name not in ("venv", "__pycache__") and child not in data_dirs:
                    # Check if directory contains non-Python files
                    include_dir = False
                    for sub in child.rglob('*'):
                        if sub.is_file() and not sub.suffix.lower() in (".py", ".pyc"):
                            include_dir = True
                            break
                    if include_dir:
                        dest = child.relative_to(bd)
                        sep = ';' if os.name == 'nt' else ':'
                        cmd += ["--add-data", f"{child}{sep}{dest}"]
                        self.log(f"📦 Added data directory: {dest}")

            # Automatically include an icon if an ICO or PNG exists in the ISO folder
            if self.iso_folder:
                for ext in ("*.ico", "*.png"):
                    found = list(self.iso_folder.glob(ext))
                    if found:
                        cmd += ["--icon", str(found[0])]
                        self.log(f"🖼 Using icon: {found[0].name}")
                        break

            # Append the entry script path to the command.  PyInstaller
            # requires a scriptname argument; without this it will
            # complain that no script was provided.
            cmd.append(str(ep))

            # Launch PyInstaller as a subprocess and stream its output to the log.
            self.log("⚙️ Running PyInstaller…")
            proc = subprocess.Popen(
                cmd,
                cwd=bd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            errors = []
            for line in proc.stdout:
                # Stream the line to the activity log (build console) and store it
                self.log(line.rstrip())
                errors.append(line)
            proc.wait()
            # Update progress bar after PyInstaller run
            self.prog.emit(70)

            # Determine if the build succeeded by checking the return code and the expected exe
            exe_filename = self.exe_name + (".exe" if sys.platform == "win32" else "")
            built = bd / "dist" / exe_filename
            if proc.returncode != 0 or not built.exists():
                # Apply fixes based on captured errors
                return self._apply_fixes(errors)

            # Copy built executable and optional ISO into output directory
            od = self.output_dir
            od.mkdir(parents=True, exist_ok=True)
            shutil.copy2(built, od / built.name)
            self.log(f"✅ Copied exe → {od / built.name}")
            if self.iso_folder:
                for f in self.iso_folder.iterdir():
                    if f.suffix.lower() == ".iso":
                        shutil.copy2(f, od / f.name)
                        self.log(f"💿 Included ISO → {f.name}")
                        break
            self.prog.emit(100)
            return True

    def _apply_fixes(self, errors) -> bool:
        """Examine build errors and prompt the user for corrective actions.

        Returns True if any fixes were applied, indicating that the build
        should be retried.  Otherwise returns False.
        """
        applied = False
        for line in errors:
            for rule in RULES:
                m = re.search(rule["pattern"], line)
                if not m:
                    continue
                applied = True
                # Apply fixes automatically without GUI pop‑ups.  GUI
                # dialogs invoked from worker threads can freeze the
                # application.  Instead we make sensible defaults: choose
                # the first display driver option, automatically add the
                # missing hidden import, ignore venv selection prompts
                # (the Worker already attempts to locate a venv), and
                # install PyInstaller automatically if missing.
                if rule["action"] == "load_display":
                    if not self.display_driver:
                        # Default to the first available display driver
                        self.display_driver = rule.get("choices", ["pandagl"])[0]
                        self.log(f"🔧 Auto‑set display driver: {self.display_driver}")
                elif rule["action"] == "hidden_import":
                    mod = m.group(1)
                    if mod not in self.hidden_imports:
                        self.hidden_imports.append(mod)
                        self.log(f"🔧 Auto‑added hidden-import={mod}")
                elif rule["action"] == "select_venv":
                    # We already try to detect venvs in __init__.  If the
                    # venv could not be found, we simply log the issue.
                    self.log("⚠️ No venv found; using current interpreter.")
                elif rule["action"] == "install_pyinstaller":
                    # Automatically install PyInstaller using pip in
                    # the selected Python interpreter.  This ensures
                    # packaging can proceed without manual intervention.
                    try:
                        self.log("🔧 Installing PyInstaller…")
                        subprocess.check_call([
                            self.venv_python,
                            "-m",
                            "pip",
                            "install",
                            "--upgrade",
                            "pyinstaller",
                        ])
                        self.log("✅ PyInstaller installed")
                    except Exception as exc:
                        self.log(f"⚠️ Failed to install PyInstaller: {exc}")
                # Ensure we mark applied so that the build process will
                # retry with our automatic fix in place
                applied = True
        return applied


# ─────────────────────────────────────────────────────────────────────
class MainWindow(QMainWindow):
    """Main application window for selecting projects and launching builds."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Interactive Panda3D Packager")
        self.setMinimumSize(900, 700)
        # Apply a dark theme via stylesheet
        self.setStyleSheet(
            """
            QWidget { background: #2d2d2d; color: #f0f0f0; font-family: Sans; }
            QPushButton { background: #006666; color: #fff; padding: 6px; border-radius: 4px; }
            QPushButton:hover { background: #008888; }
            QLineEdit, QTextEdit, QPlainTextEdit { background: #1e1e1e; color: #f0f0f0; border: 1px solid #555; }
            QProgressBar { background: #333; border: 1px solid #555; text-align: center; }
            QProgressBar::chunk { background: #00cc66; }
            QGroupBox { border: 1px solid #555; margin-top: 10px; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; }
            """
        )
        QApplication.setStyle(SlowTipStyle())
        QToolTip.setFont(QFont("Sans", 10))

        self.root = Path(__file__).parent
        (self.root / "Builds").mkdir(exist_ok=True)
        self._load_config()
        self._init_ui()

    def _load_config(self) -> None:
        cfg_file = self.root / USER_CFG
        if cfg_file.exists():
            try:
                self.cfg = json.loads(cfg_file.read_text())
            except Exception:
                self.cfg = {}
        else:
            self.cfg = {}
        # Fill in default values
        for k, d in [
            ("project_folder", ""),
            ("iso_folder", ""),
            ("entry_script", "main.py"),
            ("exe_name", ""),
            ("venv_python", ""),
        ]:
            self.cfg.setdefault(k, d)

    def _save_config(self) -> None:
        with open(self.root / USER_CFG, "w") as f:
            json.dump(self.cfg, f, indent=2)

    def _init_ui(self) -> None:
        wc = QWidget(self)
        self.setCentralWidget(wc)
        v = QVBoxLayout(wc)

        # Project folder and ISO folder selectors
        for label, key, cb in (
            ("Project Folder:", "project_folder", self._browse_proj),
            ("ISO Folder:", "iso_folder", self._browse_iso),
        ):
            h = QHBoxLayout()
            h.addWidget(QLabel(label))
            txt = QLineEdit(self.cfg[key])
            setattr(self, f"txt_{key}", txt)
            txt.textChanged.connect(lambda t, k=key: self._on_cfg(k, t))
            h.addWidget(txt, 1)
            btn = QPushButton("Browse…")
            btn.clicked.connect(cb)
            h.addWidget(btn)
            v.addLayout(h)

        # Entry script and executable name
        h2 = QHBoxLayout()
        for label, key, default in (
            ("Entry Script:", "entry_script", "main.py"),
            ("Exe Name:", "exe_name", ""),
        ):
            h2.addWidget(QLabel(label))
            txt = QLineEdit(self.cfg[key] or default)
            setattr(self, f"txt_{key}", txt)
            txt.textChanged.connect(lambda t, k=key: self._on_cfg(k, t))
            h2.addWidget(txt, 1)
        v.addLayout(h2)

        # Build / Test buttons and progress bar
        h3 = QHBoxLayout()
        self.btn_build = QPushButton("Build")
        self.btn_build.clicked.connect(self._start_build)
        h3.addWidget(self.btn_build)
        self.btn_test = QPushButton("Test Launch")
        self.btn_test.clicked.connect(self._test_launch)
        h3.addWidget(self.btn_test)
        # Button to create or ensure the output folder exists
        self.btn_create_output = QPushButton("Create Output Folder")
        self.btn_create_output.clicked.connect(self._create_output)
        h3.addWidget(self.btn_create_output)
        self.pb = QProgressBar()
        h3.addWidget(self.pb, 1)
        v.addLayout(h3)

        # Build log viewer
        v.addWidget(QLabel("Build Log:"))
        self.build_console = QTextEdit(readOnly=True)
        v.addWidget(self.build_console, 1)

        # Runtime console log viewer
        v.addWidget(QLabel("Console Log:"))
        self.game_console = QTextEdit(readOnly=True)
        v.addWidget(self.game_console, 1)

        # Builds output tree
        v.addWidget(QLabel("Builds Output:"))
        model = QFileSystemModel()
        model.setRootPath(str(self.root / "Builds"))
        tree = QTreeView()
        tree.setModel(model)
        tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        for c in range(1, model.columnCount()):
            tree.hideColumn(c)
        v.addWidget(tree, 1)

        # Practices editor
        grp = QGroupBox("Packaging Practices")
        lay = QVBoxLayout(grp)
        btn_c = QPushButton("Create Practices File")
        btn_c.clicked.connect(self._create_practices_file)
        lay.addWidget(btn_c)
        h4 = QHBoxLayout()
        self.prac_in = QLineEdit()
        self.prac_in.setPlaceholderText("Enter practice/problem…")
        h4.addWidget(self.prac_in)
        btn_a = QPushButton("Add to File")
        btn_a.clicked.connect(self._add_practice)
        h4.addWidget(btn_a)
        lay.addLayout(h4)
        btn_cp = QPushButton("Copy Practices to Clipboard")
        btn_cp.clicked.connect(self._copy_practices)
        lay.addWidget(btn_cp)
        v.addWidget(grp)

        # Ollama model selection and auto patcher
        ollama_grp = QGroupBox("Ollama & Auto Patcher")
        ollama_layout = QVBoxLayout(ollama_grp)
        # Dropdown to select an Ollama model.  Prepopulate with a few example models.
        model_row = QHBoxLayout()
        model_row.addWidget(QLabel("Ollama Model:"))
        self.ollama_combo = QComboBox()
        self.ollama_combo.addItems([
            "phi4:latest",
            "mistral:latest",
            "llama:latest",
            "codellama:latest",
        ])
        model_row.addWidget(self.ollama_combo, 1)
        ollama_layout.addLayout(model_row)
        # Button to create an auto patcher batch file
        btn_patch = QPushButton("Create Auto Patcher")
        btn_patch.clicked.connect(self._create_auto_patcher)
        ollama_layout.addWidget(btn_patch)
        v.addWidget(ollama_grp)

    def _on_cfg(self, key: str, val: str) -> None:
        self.cfg[key] = val
        self._save_config()

    def _browse_proj(self) -> None:
        d = QFileDialog.getExistingDirectory(self, "Select Project Folder", "")
        if d:
            self.txt_project_folder.setText(d)

    def _browse_iso(self) -> None:
        d = QFileDialog.getExistingDirectory(self, "Select ISO Folder", "")
        if d:
            self.txt_iso_folder.setText(d)

    def _log_activity(self, msg: str) -> None:
        # Append runtime (console) messages
        self.game_console.append(msg)

    def _log_build(self, msg: str) -> None:
        """
        Append a message to the build log view and persist it to
        build.log.  Messages originating from the Worker (via the
        activity signal) are routed here during the build process.
        """
        self.build_console.append(msg)
        # Persist the build log so it can be inspected later.  Use
        # UTF‑8 encoding and ignore errors to avoid Unicode issues on
        # platforms with non‑UTF encodings (e.g. Windows cp1252).
        try:
            with open(BUILD_LOG, "a", encoding="utf-8", errors="ignore") as f:
                f.write(msg + "\n")
        except Exception:
            pass

    def _start_build(self) -> None:
        # Clear logs
        self.game_console.clear()
        self.build_console.clear()
        for f in (ACTIVITY_LOG, BUILD_LOG):
            try:
                open(f, "w").close()
            except Exception:
                pass

        worker = Worker(self.cfg)
        thread = QThread(self)
        # Build messages emitted by Worker.log (via activity signal) should go
        # to the build console.  During a build we want to keep runtime logs
        # separate from build logs, so connect to _log_build instead of
        # _log_activity.
        worker.activity.connect(self._log_build)
        worker.prog.connect(self.pb.setValue)
        worker.done.connect(lambda: self._log_build("✅ Build succeeded."))
        worker.err.connect(lambda tb: self._log_build(tb))

        # We no longer instantiate BuildWindow within the worker; build
        # output is streamed back via the worker's activity signal.  No
        # monkey‑patching is needed here.

        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        thread.start()
        self.btn_build.setEnabled(False)
        thread.finished.connect(lambda: self.btn_build.setEnabled(True))

    def _test_launch(self) -> None:
        exe = Path("Builds") / self.cfg["exe_name"] / (
            self.cfg["exe_name"] + (".exe" if sys.platform == "win32" else "")
        )
        if not exe.exists():
            QMessageBox.warning(self, "Error", "No built exe found.")
            return
        self._log_activity(f"🚀 Launching {exe.name}…")
        proc = subprocess.Popen(
            [str(exe)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        def reader():
            for line in proc.stdout:
                self._log_activity(line.rstrip())
                try:
                    with open(TEST_LOG, "a", encoding="utf-8", errors="ignore") as f:
                        f.write(line)
                except Exception:
                    pass
            self._log_activity(f"🏁 Process exited code {proc.wait()}")
        import threading
        threading.Thread(target=reader, daemon=True).start()

    def _create_practices_file(self) -> None:
        p = self.root / PRACTICES
        if not p.exists():
            p.write_text("")
        QMessageBox.information(self, "Practices", f"{PRACTICES} is ready.")

    def _add_practice(self) -> None:
        t = self.prac_in.text().strip()
        if not t:
            QMessageBox.warning(self, "Empty", "Enter something first.")
            return
        p = self.root / PRACTICES
        if not p.exists():
            QMessageBox.warning(self, "Missing", "Create file first.")
            return
        with open(p, "a") as f:
            f.write(t + "\n")
        self.prac_in.clear()
        QMessageBox.information(self, "Added", f"“{t}” appended.")

    def _copy_practices(self) -> None:
        p = self.root / PRACTICES
        if not p.exists():
            QMessageBox.warning(self, "Missing", "No practices file.")
            return
        QApplication.clipboard().setText(p.read_text())
        QMessageBox.information(self, "Copied", "Practices copied.")

    def _create_output(self) -> None:
        """Create (or ensure) the output folder for the current project.

        This folder resides under the script's Builds directory and is
        named after the executable (or project) name.  Creating the
        folder ahead of time allows the user to inspect or populate it
        before building.
        """
        # Determine the executable name from the configuration.  If
        # none is provided, fall back to the project folder's name.
        exe_name = self.cfg.get("exe_name") or (Path(self.cfg.get("project_folder") or "").name or "Untitled")
        # Compute the absolute output directory using the script's root
        out_dir = Path(__file__).parent / "Builds" / exe_name
        out_dir.mkdir(parents=True, exist_ok=True)
        # Inform the user that the directory is ready
        QMessageBox.information(self, "Output Folder", f"Output folder created:\n{out_dir}")
        # Log this action to the build log
        self._log_build(f"📁 Created output folder {out_dir}")

    def _create_auto_patcher(self) -> None:
        """
        Generate an auto_patcher.bat script in the packager root.

        The script activates the project's virtual environment and upgrades
        pip and pyinstaller.  The selected Ollama model is noted in a
        comment for reference, but no call to the model is made because
        this environment cannot interact with external AI services.
        """
        model = self.ollama_combo.currentText()
        # Determine project and venv paths
        project_folder = self.cfg.get("project_folder") or ""
        proj = Path(project_folder) if project_folder else None
        if not proj or not proj.exists():
            QMessageBox.warning(self, "Error", "Select a valid project folder first.")
            return
        # Build path to the venv activation script (Windows).  On Unix
        # systems the activation script is in bin/activate, but this
        # script is tailored for Windows environments.
        venv_act = proj / "venv" / "Scripts" / "activate"
        # Path to create auto_patcher.bat in the packager root
        bat_path = Path(__file__).parent / "auto_patcher.bat"
        try:
            with open(bat_path, "w", encoding="utf-8") as f:
                # Begin the batch script.  Use descriptive comments to aid
                # troubleshooting.  The script activates the project's
                # virtual environment, upgrades pip and PyInstaller, and
                # optionally installs dependencies from requirements.txt
                f.write("@echo off\n")
                f.write(f"REM Auto-generated patcher using model: {model}\n")
                f.write(f"REM Project folder: {proj}\n")
                f.write(f"CALL \"{venv_act}\"\n")
                # Upgrade pip and PyInstaller
                f.write("python -m pip install --upgrade pip\n")
                f.write("python -m pip install --upgrade pyinstaller\n")
                # Install requirements if a requirements.txt file is present in the project
                req_path = proj / "requirements.txt"
                if req_path.exists():
                    # Use Windows batch syntax to check for the file before installing
                    f.write(f"IF EXIST \"{req_path}\" (\n")
                    f.write(f"    python -m pip install -r \"{req_path}\"\n")
                    f.write(")\n")
            QMessageBox.information(self, "Auto Patcher", f"auto_patcher.bat created:\n{bat_path}")
            self._log_build(f"🛠️ Created auto patcher at {bat_path}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to create auto_patcher.bat:\n{e}")


def exception_handler(t, v, tb) -> None:
    """Display an error dialog with copy and close buttons for uncaught exceptions."""
    err_text = "".join(traceback.format_exception(t, v, tb))
    # Create a custom dialog instead of a simple message box so we can
    # include a copy button.  The dialog owns a read‑only text edit
    # containing the traceback.  Two buttons are provided: one to copy
    # the traceback to the clipboard and one to close the dialog.
    dlg = QDialog()
    dlg.setWindowTitle("Fatal Error")
    dlg.resize(700, 500)
    layout = QVBoxLayout(dlg)
    text_widget = QPlainTextEdit(err_text)
    text_widget.setReadOnly(True)
    layout.addWidget(text_widget, 1)
    # Button box with Copy and Close buttons
    btn_box = QDialogButtonBox()
    copy_btn = QPushButton("Copy")
    close_btn = QPushButton("Close")
    btn_box.addButton(copy_btn, QDialogButtonBox.ActionRole)
    btn_box.addButton(close_btn, QDialogButtonBox.RejectRole)
    def copy_to_clipboard():
        QApplication.clipboard().setText(err_text)
    copy_btn.clicked.connect(copy_to_clipboard)
    close_btn.clicked.connect(dlg.reject)
    layout.addWidget(btn_box)
    dlg.exec_()


sys.excepthook = exception_handler


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
```

This script provides a GUI front‑end for packaging Panda3D games into
self‑contained executables.  It clones a project into a temporary
directory, invokes PyInstaller to build a one‑file binary and then
optionally retries with user‑supplied fixes if the build fails.  The
script has been enhanced to better handle Panda3D projects: it will
automatically discover a project‑local virtual environment, include
data directories (e.g. models or textures) via PyInstaller's
``--add-data`` option and collect all resources from the ``panda3d``
package.
**Classes:** SlowTipStyle, BuildWindow, Worker, MainWindow
**Functions:** qt_message_handler(msg_type, ctx, msg), clean_clone(src, dst, log_fn), exception_handler(t, v, tb)


## Module `Projects\TestGame3D\clone\main.py`

```python
#!/usr/bin/env python3
# Enhanced Fantasy RPG - Knight's Quest (ASCII only), 2025-07-24

import sys, random
from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import DirectWaitBar, DirectFrame, DirectButton
from panda3d.core import WindowProperties, TextNode, CardMaker
from direct.gui.OnscreenText import OnscreenText
from direct.task import Task

class Item:
    def __init__(self, name, effect_type, value, description, rarity="common"):
        self.name = name
        self.effect_type = effect_type  # "heal", "damage", "buff"
        self.value = value
        self.description = description
        self.rarity = rarity
        self.rarity_colors = {
            "common":    (0.8, 0.8, 0.8, 1),
            "rare":      (0.3, 0.8, 0.3, 1),
            "epic":      (0.6, 0.3, 0.9, 1),
            "legendary": (1, 0.8, 0.2, 1)
        }

    def get_color(self):
        return self.rarity_colors.get(self.rarity, (1,1,1,1))

class Character:
    def __init__(self, name, hp, stamina, mana, attacks, color, level=1):
        self.name = name
        self.level = level
        self.max_hp = hp
        self.hp = hp
        self.max_stamina = stamina
        self.stamina = stamina
        self.max_mana = mana
        self.mana = mana
        self.attacks = attacks  # list of tuples: (label, cost_type, cost, range, effect)
        self.color = color
        self.exp = 0
        self.max_exp = 100
        self.gold = 0
        self.status_effects = {}  # e.g. {"poison": remaining_turns}

    def is_alive(self):
        return self.hp > 0

    def perform(self, attack, target=None):
        label, cost_type, cost, rng, effect = attack
        # Resource check
        if cost_type == "stamina" and self.stamina < cost:
            return None, "Not enough stamina!"
        if cost_type == "mana" and self.mana < cost:
            return None, "Not enough mana!"
        # Pay cost
        if cost_type == "stamina":
            self.stamina -= cost
        else:
            self.mana -= cost
        # Handle effect
        if effect == "heal":
            amt = random.randint(*rng)
            self.hp = min(self.max_hp, self.hp + amt)
            return ("heal", amt), None
        if effect == "mana_restore":
            amt = random.randint(*rng)
            self.mana = min(self.max_mana, self.mana + amt)
            return ("mana", amt), None
        if effect in ("poison", "burn"):
            amt = random.randint(*rng)
            target.hp = max(0, target.hp - amt)
            duration = 3 if effect == "poison" else 2
            target.status_effects[effect] = duration
            return (effect, amt), None
        # Regular damage with crit chance
        dmg = random.randint(*rng)
        if random.random() < 0.15:
            dmg = int(dmg * 1.5)
            target.hp = max(0, target.hp - dmg)
            return ("crit", dmg), None
        target.hp = max(0, target.hp - dmg)
        return ("damage", dmg), None

class EnhancedRPG(ShowBase):
    def __init__(self):
        super().__init__()
        self.disableMouse()

        # Window setup
        props = WindowProperties()
        props.setTitle("Knight's Quest - ASCII UI")
        props.setSize(1200, 800)
        self.win.requestProperties(props)

        # Background
        self.create_background()

        # ASCII Art
        self.define_ascii_art()

        # Build characters
        self.build_characters()

        # Inventory
        self.inventory = [
            Item("Potion", "heal", 25, "Restores 25 HP", "common"),
            Item("Elixir", "mana", 20, "Restores 20 MP", "common"),
            Item("Bomb", "damage", 30, "Deals 30 damage", "rare")
        ]

        # UI and game state
        self.setup_ui()
        self.setup_game_state()

        # Start with first enemy
        self.load_enemy(0)

    def create_background(self):
        cm = CardMaker("bg")
        cm.setFrame(-2, 2, -2, 2)
        bg = self.render2d.attachNewNode(cm.generate())
        bg.setColor(0.05, 0.05, 0.05, 1)
        bg.setBin("background", 0)

    def define_ascii_art(self):
        self.art_player = {
            "idle":   " O \n/|\\\n/ \\",
            "attack": "\\O/   \n |    \n/ \\"
        }
        self.art_enemies = {
            "Goblin": " ^_^\n(o_o)\n/| |\\",
            "Orc":    " (O)\n/|\\ \n/ \\",
            "Bat":    " ( )\n(o o)\n -- ",
        }

    def build_characters(self):
        self.player = Character(
            "Sir Galahad", 100, 50, 40,
            [
                ("Slash", "stamina", 8, (12, 18), "damage"),
                ("Bash", "stamina", 12, (8, 22), "damage"),
                ("Heal", "mana", 15, (15, 25), "heal")
            ],
            (0.5, 0.7, 1, 1)
        )
        self.enemies = [
            Character("Goblin", 45, 25, 15, [("Claw", "stamina", 0, (6, 12), "damage")], (0.5, 1, 0.5, 1)),
            Character("Orc",    80, 40, 10, [("Smash", "stamina", 0, (10, 16), "damage")], (1, 0.5, 0.5, 1)),
            Character("Bat",    35, 30, 25, [("Bite", "mana", 5, (4, 10), "damage")], (0.7, 0.7, 0.7, 1))
        ]
        self.e_idx = 0
        self.enemy = None

    def setup_ui(self):
        # Main frame
        self.frame = DirectFrame(
            frameColor=(0.1, 0.1, 0.15, 0.9),
            frameSize=(-1.4, 1.4, -1, 1),
            parent=self.aspect2d
        )

        # Player ASCII art
        self.txt_player = OnscreenText(
            text=self.art_player["idle"],
            pos=(-0.8, 0.3), scale=0.06,
            fg=self.player.color,
            align=TextNode.ACenter,
            mayChange=True,
            parent=self.frame
        )

        # Enemy ASCII art
        self.txt_enemy = OnscreenText(
            text="",
            pos=(0.8, 0.3), scale=0.06,
            fg=(1,1,1,1),
            align=TextNode.ACenter,
            mayChange=True,
            parent=self.frame
        )

        # Player HP bar
        self.hp_bar = DirectWaitBar(
            text="HP", value=self.player.hp, range=self.player.max_hp,
            barColor=(0.8, 0.1, 0.1, 1),
            frameColor=(1,1,1,1),
            parent=self.frame
        )
        self.hp_bar.setScale(0.6, 1, 0.04)
        self.hp_bar.setPos(0, 0, 0.9)

        # Player Stamina bar
        self.sta_bar = DirectWaitBar(
            text="STA", value=self.player.stamina, range=self.player.max_stamina,
            barColor=(0.2, 0.8, 0.2, 1),
            frameColor=(1,1,1,1),
            parent=self.frame
        )
        self.sta_bar.setScale(0.6, 1, 0.04)
        self.sta_bar.setPos(0, 0, 0.83)

        # Enemy HP bar
        self.ehp_bar = DirectWaitBar(
            text="HP", value=0, range=1,
            barColor=(1, 0.3, 0.3, 1),
            frameColor=(1,1,1,1),
            parent=self.frame
        )
        self.ehp_bar.setScale(0.6, 1, 0.04)
        self.ehp_bar.setPos(0, 0, 0.76)

        # Inventory display
        inv_text = "Inventory: " + ", ".join(item.name for item in self.inventory)
        self.txt_inv = OnscreenText(
            text=inv_text,
            pos=(-1.3, -0.7), scale=0.05,
            fg=(1,1,1,1),
            align=TextNode.ALeft,
            parent=self.frame
        )

        # Attack buttons
        self.buttons = []
        for i, atk in enumerate(self.player.attacks):
            name, _, cost, _, _ = atk
            btn = DirectButton(
                text=f"{name}({cost})",
                scale=0.05,
                pos=(-0.6 + i*0.6, 0, -0.4),
                parent=self.frame,
                command=self.on_attack,
                extraArgs=[i]
            )
            self.buttons.append(btn)

        # Battle log
        self.log = []
        self.txt_log = OnscreenText(
            text="-- Battle Log --",
            pos=(0, -0.9), scale=0.05,
            fg=(1,1,1,1),
            align=TextNode.ACenter,
            parent=self.frame
        )

    def setup_game_state(self):
        self.player_turn = True
        self.game_over = False
        self.accept('r', self.next_enemy)
        self.accept('q', sys.exit)
        self.taskMgr.add(self.update, "updateTask")

    def load_enemy(self, idx):
        if idx >= len(self.enemies):
            self.append_log("You vanquished all foes! Victory!")
            self.game_over = True
            return
        self.enemy = self.enemies[idx]
        self.enemy.hp = self.enemy.max_hp
        art = self.art_enemies.get(self.enemy.name, "??")
        self.txt_enemy.setText(art)
        self.ehp_bar['range'] = self.enemy.max_hp
        self.ehp_bar['value'] = self.enemy.hp
        self.append_log(f"A wild {self.enemy.name} appears!")
        self.player_turn = True

    def append_log(self, msg):
        self.log.append(msg)
        if len(self.log) > 5:
            self.log.pop(0)
        self.txt_log.setText("\n".join(self.log))

    def on_attack(self, idx):
        if not self.player_turn or self.game_over:
            return
        atk, err = self.player.perform(self.player.attacks[idx], self.enemy)
        if err:
            self.append_log(err)
            return
        kind, amt = atk
        name = self.player.attacks[idx][0]
        if kind == "heal":
            self.append_log(f"{name} heals {amt} HP")
        else:
            self.append_log(f"{name} hits for {amt} damage")
        # Update bars
        self.hp_bar['value'] = self.player.hp
        self.sta_bar['value'] = self.player.stamina
        self.ehp_bar['value'] = self.enemy.hp
        self.player_turn = False
        if not self.enemy.is_alive():
            self.append_log(f"{self.enemy.name} defeated!")
            self.taskMgr.doMethodLater(1, lambda t: self.next_enemy(), "nextEnemy")
        else:
            self.taskMgr.doMethodLater(1, self.enemy_turn, "enemyTurn")

    def enemy_turn(self, task):
        atk, err = self.enemy.perform(self.enemy.attacks[0], self.player)
        kind, amt = atk
        name = self.enemy.attacks[0][0]
        self.append_log(f"{self.enemy.name} {name} for {amt} damage")
        self.hp_bar['value'] = self.player.hp
        if not self.player.is_alive():
            self.append_log("You have fallen... Game Over.")
            self.game_over = True
        else:
            self.player_turn = True
        return Task.done

    def next_enemy(self, arg=None):
        self.e_idx += 1
        self.load_enemy(self.e_idx)

    def update(self, task):
        # Apply status effects
        for effect in list(self.player.status_effects):
            if effect == "poison":
                self.player.hp = max(0, self.player.hp - 5)
                self.append_log("Poison deals 5 damage")
            if effect == "burn":
                self.player.hp = max(0, self.player.hp - 7)
                self.append_log("Burn deals 7 damage")
            self.player.status_effects[effect] -= 1
            if self.player.status_effects[effect] <= 0:
                del self.player.status_effects[effect]
        # Refresh bars
        self.hp_bar['value'] = self.player.hp
        self.sta_bar['value'] = self.player.stamina
        self.ehp_bar['value'] = self.enemy.hp if self.enemy else 0
        return Task.cont

def main():
    game = EnhancedRPG()
    game.run()

if __name__ == "__main__":
    main()
```

**Classes:** Item, Character, EnhancedRPG
**Functions:** main()


## Module `sdk\tools\codesigning\build_steam_signatures_file.py`

```python
import os
import io
import sys
import re

# wrapper for print
def printw( message ):
    print( message )

try:
    import Crypto
    from Crypto.Signature import PKCS1_v1_5
    from Crypto.Hash import SHA
    from Crypto.PublicKey import RSA
except Exception as e:
    printw( "Missing required module: "+str(e) )
    sys.exit( -1 )
    
try:
    import zlib
except Exception as e:
    printw( "Missing required module: "+str(e) )
    sys.exit( -1 )

try:
    import hashlib
except Exception as e:
    printw( "Missing required module: "+str(e) )
    sys.exit( -1 )

try:
    import ctypes
except Exception as e:
    printw( "Missing required module: "+str(e) )
    sys.exit( -1 )


def usage():
    printw( "usage to verify a signaturefile:"+ sys.argv[0]+ " signaturefile publickeyfile" )
    printw( "usage to write a new signaturefile:"+ sys.argv[0]+ " signaturefile publickeyfile privatekeyfile newfilename" )
    printw( "" )

def readkeyfile( publickeyfilename ):
    # read the public key file.
    rawkey = open(publickeyfilename, mode='rb').read()
    # import as an RSA key
    key = RSA.importKey(rawkey)
    return key

def signmessage_add_digest( message, privatekeyfile ):
    key = RSA.importKey(open( privatekeyfile, mode='rb' ).read())
    h = SHA.new(message)
    signer = PKCS1_v1_5.new(key)
    signature = signer.sign(h)
    sighex = signature.encode("hex")
    return "DIGEST:"+sighex.upper()+"\r\n"

def checkdigest( signaturefilename, key ):
    with open(signaturefilename, mode='rb') as file:
        fileContent = file.read()

    # find the start of the digest
    idxtodigest = fileContent.find('DIGEST:')
    if idxtodigest == 0:
        return 0

    # the message is everything else
    message = fileContent[0:idxtodigest]

    digestpart = fileContent[idxtodigest+7:]
    digestpart = digestpart.replace("\r\n","")
    signature = digestpart.decode("hex")

    try:
        h = SHA.new(message)
        verifier = PKCS1_v1_5.new(key)
        if not verifier.verify(h, signature):
            return 0
    except Exception as e:
        printw( "could not verify signature: "+str(e) )
    return message

def crchex( crc32 ):
    crc32b = ctypes.c_uint32(crc32).value
    crc32hex = hex(crc32b).upper().replace("0X","").replace("L","")
    lenhex = len(crc32hex)
    # pad to 8 chars with leading 0s
    padding = 8 - lenhex
    while padding:
        crc32hex = "0"+crc32hex
        padding = padding - 1
    # byte swap
    crc32hex_reverse = crc32hex[6:8]+crc32hex[4:6]+crc32hex[2:4]+crc32hex[0:2]
    return crc32hex_reverse

def parsehashes( message, pathto ):
    # now verify all the file hashes
    newmessage = ""
    lines = message.split("\r\n")
    for line in lines:
        if len(line) == 0:
            break
        # parse the line, should be 5 parts
        # filename "~SHA1" sha1 ";CRC:" crc32
        parts=re.split(';|:|~',line)
        if len(parts) != 5:
            printw( "The file format is unexpected line:"+line )
            break
        if parts[1] != "SHA1" or parts[3] != "CRC":
            printw( "The file format is unexpected line:"+line )
            break

        hashprovided = parts[2]
        crcprovided = parts[4]
        onefile = parts[0]
        onefile = onefile.replace("...\\","")
        onefilepath = os.path.join( pathto, onefile )
        try:
            with open(onefilepath, mode='rb') as file:
                targetcontent = file.read()
        except:
            printw( "could not open: "+onefilepath )
            continue

        # compute sha1 of file
        mm = hashlib.sha1()
        mm.update(targetcontent)
        newhash = mm.hexdigest().upper()
        # compute crc32 of file
        crc32 = zlib.crc32(targetcontent)
        crc32hex = crchex(crc32)
        if ( newhash == hashprovided.upper() and
                crc32hex == crcprovided.upper() ):
            printw( "The hashes are correct for "+onefile )
        else:
            printw( "The hashes are different for "+onefile+" sha: "+newhash+" "+hashprovided.upper()+" CRC "+crc32hex+" "+crcprovided.upper() )
        # accumulate new hashes
        linenew = "...\\"+onefile+"~SHA1:"+newhash+";CRC:"+crc32hex+"\r\n"
        newmessage += linenew

    return newmessage

def signatures_need_update( signaturefilename, publickeyfilename ):

    if not os.path.exists( signaturefilename ):
        printw( "Signature file does not exist" )
        sys.stdout.flush()
        return False

    pathto = os.path.split(signaturefilename)[0]

    if not os.path.exists( publickeyfilename ):
        printw( "Public key file does not exist" )
        sys.stdout.flush()
        return False

    key = readkeyfile( publickeyfilename )

    message = checkdigest( signaturefilename, key )
    if len(message) == 0:
        printw( "failed to parse signature file " )
        return False

    newmessage = parsehashes( message, pathto )
    if len(newmessage) == 0:
        printw( "failed to parse hashes in signature data " )
        return False
    return newmessage != message


def write_new_signature_file( signaturefilename, publickeyfilename, privatekeyfilename, newsignaturefilename ):

    if not os.path.exists( signaturefilename ):
        printw( "Signature file does not exist" )
        sys.stdout.flush()
        return -1

    pathto = os.path.split(signaturefilename)[0]

    if not os.path.exists( publickeyfilename ):
        printw( "Public key file does not exist" )
        sys.stdout.flush()
        return -2

    if not os.path.exists( privatekeyfilename ):
        printw( "Private key file does not exist" )
        sys.stdout.flush()
        return -3

    if os.path.exists( newsignaturefilename ) and not os.access( newsignaturefilename, os.W_OK ):
        printw( "new signatures file not writeable " )
        sys.stdout.flush()
        return -4

    key = readkeyfile( publickeyfilename )

    message = checkdigest( signaturefilename, key )
    if len(message) == 0:
        printw( "failed to parse old signature file " )
        return -5

    newmessage = parsehashes( message, pathto )
    if len(newmessage) == 0:
        printw( "failed to create new signature data " )
        return -6

    with open( newsignaturefilename, mode='wb') as file:
        file.write( newmessage )
        hexdigest = signmessage_add_digest( newmessage, privatekeyfilename )
        file.write( hexdigest )

    printw( "new signatures file written successfully " )
    sys.stdout.flush()
    return 0


def main():

    if len( sys.argv ) != 5 and len( sys.argv ) != 3:
        usage()
        sys.exit(2)

    # common args
    signaturefilename = sys.argv[1]
    publickeyfilename = sys.argv[2]

    if len( sys.argv ) == 5:
        # only if writing a new file
        privatekeyfilename = sys.argv[3]
        newsignaturefilename = sys.argv[4]
        write_new_signature_file( signaturefilename, publickeyfilename, privatekeyfilename, newsignaturefilename )
    else:
        if signatures_need_update( signaturefilename, publickeyfilename ):
            printw( "Some signatures did not match" )
        else:
            printw( "All signatures matched" )


if __name__ == '__main__':
    main()
```

**Functions:** printw(message), usage(), readkeyfile(publickeyfilename), signmessage_add_digest(message, privatekeyfile), checkdigest(signaturefilename, key), crchex(crc32), parsehashes(message, pathto), signatures_need_update(signaturefilename, publickeyfilename), write_new_signature_file(signaturefilename, publickeyfilename, privatekeyfilename, newsignaturefilename), main()
