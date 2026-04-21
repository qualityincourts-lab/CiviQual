#!/usr/bin/env python3
"""
CiviQual Stats Installer Build Script

This script builds the CiviQual Stats application and creates a Windows installer.

Requirements:
- Python 3.9+
- PyInstaller (pip install pyinstaller)
- Pillow (pip install pillow) - for icon conversion
- Inno Setup 6+ (https://jrsoftware.org/isinfo.php) - for installer creation

Usage:
    python build_installer.py exe        # Build executable only
    python build_installer.py installer  # Build installer (requires exe first)
    python build_installer.py all        # Build everything
    python build_installer.py clean      # Clean build artifacts

Copyright (c) 2026 A Step in the Right Direction LLC
All Rights Reserved.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


class CiviQualStatsInstallerBuilder:
    """Builds CiviQual Stats executable and Windows installer."""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.dist_dir = self.root_dir / "dist"
        self.build_dir = self.root_dir / "build"
        self.installer_dir = self.root_dir / "installer"
        self.output_dir = self.installer_dir / "output"
        
        # Application info
        self.app_name = "CiviQualStats"
        self.app_version = "1.2.0"
        
    def clean(self):
        """Clean previous build artifacts."""
        print("Cleaning previous builds...")
        
        for dir_path in [self.dist_dir, self.build_dir, self.output_dir]:
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"  Removed: {dir_path}")
        
        # Remove spec file
        spec_file = self.root_dir / f"{self.app_name}.spec"
        if spec_file.exists():
            spec_file.unlink()
            print(f"  Removed: {spec_file}")
            
        print("Clean complete.\n")
    
    def create_icon(self):
        """Convert PNG icon to ICO format for Windows."""
        print("Creating Windows icon file...")
        
        png_path = self.root_dir / "civiqual_icon.png"
        ico_path = self.root_dir / "civiqual_icon.ico"
        installer_ico = self.installer_dir / "civiqual_icon.ico"
        
        if not png_path.exists():
            print(f"  Warning: {png_path} not found. Generating icon...")
            self._generate_icon_png(png_path)
        
        try:
            from PIL import Image
            
            img = Image.open(png_path)
            
            # Create ICO with multiple sizes
            sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
            icon_images = []
            
            for size in sizes:
                resized = img.resize(size, Image.Resampling.LANCZOS)
                icon_images.append(resized)
            
            icon_images[0].save(
                ico_path,
                format='ICO',
                sizes=[(img.width, img.height) for img in icon_images],
                append_images=icon_images[1:]
            )
            
            # Copy to installer directory
            shutil.copy2(ico_path, installer_ico)
            
            print(f"  Created: {ico_path}")
            print(f"  Copied to: {installer_ico}")
            
        except ImportError:
            print("  Warning: Pillow not installed. Skipping icon creation.")
            print("  Install with: pip install pillow")
    
    def _generate_icon_png(self, output_path):
        """Generate CiviQual Stats icon PNG file."""
        try:
            import matplotlib.pyplot as plt
            import matplotlib.patches as patches
            
            # CiviQual Brand Colors
            BURGUNDY = '#6d132a'
            GOLD = '#dcad73'
            
            fig, ax = plt.subplots(figsize=(5.12, 5.12), dpi=100)
            ax.set_xlim(0, 100)
            ax.set_ylim(0, 100)
            ax.set_aspect('equal')
            ax.axis('off')
            
            # Background
            bg = patches.FancyBboxPatch((2, 2), 96, 96, 
                                         boxstyle="round,pad=0,rounding_size=12",
                                         facecolor=BURGUNDY, edgecolor='none')
            ax.add_patch(bg)
            
            # Inner white square
            inner = patches.FancyBboxPatch((8, 8), 84, 84,
                                            boxstyle="round,pad=0,rounding_size=8",
                                            facecolor='white', edgecolor='none')
            ax.add_patch(inner)
            
            # Dividing lines
            ax.plot([50, 50], [10, 90], color=BURGUNDY, linewidth=3)
            ax.plot([10, 90], [50, 50], color=BURGUNDY, linewidth=3)
            
            # Quadrant elements (simplified)
            # Top-left: histogram bars
            for x, h in [(18, 20), (26, 30), (34, 40), (42, 28)]:
                ax.add_patch(patches.Rectangle((x, 52), 6, h, facecolor=GOLD))
            
            # Top-right: probability line
            ax.plot([55, 90], [55, 90], color=GOLD, linewidth=3)
            
            # Bottom-left: I-chart line
            ax.plot([15, 45], [30, 30], color=BURGUNDY, linewidth=2)
            ax.plot([15, 25, 30, 35, 40, 45], [30, 35, 25, 32, 28, 30], 
                   color=GOLD, linewidth=2, marker='o', markersize=4)
            
            # Bottom-right: bell curve
            import numpy as np
            x = np.linspace(55, 95, 50)
            y = 15 + 20 * np.exp(-((x - 75)**2) / 100)
            ax.plot(x, y, color=GOLD, linewidth=3)
            
            plt.savefig(output_path, dpi=100, bbox_inches='tight', 
                       facecolor='white', pad_inches=0)
            plt.close()
            
            print(f"  Generated: {output_path}")
            
        except ImportError:
            print("  Error: matplotlib required to generate icon")
    
    def build_executable(self):
        """Build the Windows executable using PyInstaller."""
        print("\nBuilding Windows executable...")
        
        # Create icon first
        self.create_icon()
        
        ico_path = self.root_dir / "civiqual_icon.ico"
        
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--name", self.app_name,
            "--onefile",
            "--windowed",
            "--noconfirm",
            "--clean",
        ]
        
        # Add icon if available
        if ico_path.exists():
            cmd.extend(["--icon", str(ico_path)])
        
        # Add data files
        data_files = [
            ("civiqual_icon.png", "."),
            ("sample_data.csv", "."),
            ("LICENSE", "."),
            ("README.md", "."),
            ("SECTION_508_COMPLIANCE.md", "."),
        ]
        
        for src, dst in data_files:
            src_path = self.root_dir / src
            if src_path.exists():
                sep = ";" if sys.platform == "win32" else ":"
                cmd.extend(["--add-data", f"{src_path}{sep}{dst}"])
        
        # Hidden imports
        hidden_imports = [
            "PySide6.QtCore",
            "PySide6.QtGui", 
            "PySide6.QtWidgets",
            "pandas",
            "numpy",
            "scipy",
            "scipy.stats",
            "matplotlib",
            "matplotlib.backends.backend_qtagg",
        ]
        
        for imp in hidden_imports:
            cmd.extend(["--hidden-import", imp])
        
        cmd.append(str(self.root_dir / "main.py"))
        
        print(f"  Command: {' '.join(cmd[:10])}...")
        
        result = subprocess.run(cmd, cwd=self.root_dir)
        
        if result.returncode != 0:
            print("ERROR: PyInstaller build failed!")
            return False
        
        exe_path = self.dist_dir / f"{self.app_name}.exe"
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"\nExecutable created: {exe_path}")
            print(f"Size: {size_mb:.1f} MB")
            return True
        else:
            print("ERROR: Executable not found after build!")
            return False
    
    def build_installer(self):
        """Build the Windows installer using Inno Setup."""
        print("\nBuilding Windows installer...")
        
        exe_path = self.dist_dir / f"{self.app_name}.exe"
        if not exe_path.exists():
            print("ERROR: Executable not found. Run 'build_installer.py exe' first.")
            return False
        
        # Find Inno Setup compiler
        inno_paths = [
            Path(r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"),
            Path(r"C:\Program Files\Inno Setup 6\ISCC.exe"),
            Path(r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe"),
            Path(r"C:\Program Files\Inno Setup 5\ISCC.exe"),
        ]
        
        iscc_path = None
        for path in inno_paths:
            if path.exists():
                iscc_path = path
                break
        
        if iscc_path is None:
            print("ERROR: Inno Setup not found!")
            print("Please install Inno Setup from: https://jrsoftware.org/isinfo.php")
            print("\nAlternatively, compile manually:")
            print(f"  1. Open Inno Setup Compiler")
            print(f"  2. Open: {self.installer_dir / 'CiviQualStats_Setup.iss'}")
            print(f"  3. Click Build > Compile")
            return False
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy icon to installer directory
        ico_src = self.root_dir / "civiqual_icon.ico"
        ico_dst = self.installer_dir / "civiqual_icon.ico"
        if ico_src.exists():
            shutil.copy2(ico_src, ico_dst)
        
        iss_path = self.installer_dir / "CiviQualStats_Setup.iss"
        
        cmd = [str(iscc_path), str(iss_path)]
        print(f"  Command: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, cwd=self.installer_dir)
        
        if result.returncode != 0:
            print("ERROR: Installer build failed!")
            return False
        
        for file in self.output_dir.glob("CiviQualStats_Setup_*.exe"):
            size_mb = file.stat().st_size / (1024 * 1024)
            print(f"\nInstaller created: {file}")
            print(f"Size: {size_mb:.1f} MB")
            return True
        
        print("ERROR: Installer not found after build!")
        return False
    
    def create_portable_zip(self):
        """Create a portable ZIP distribution."""
        print("\nCreating portable ZIP distribution...")
        
        exe_path = self.dist_dir / f"{self.app_name}.exe"
        if not exe_path.exists():
            print("ERROR: Executable not found. Run 'build_installer.py exe' first.")
            return False
        
        import zipfile
        
        zip_path = self.dist_dir / f"CiviQualStats_Portable_{self.app_version}.zip"
        
        files_to_include = [
            (exe_path, "CiviQualStats.exe"),
            (self.root_dir / "civiqual_icon.png", "civiqual_icon.png"),
            (self.root_dir / "LICENSE", "LICENSE"),
            (self.root_dir / "README.md", "README.md"),
            (self.root_dir / "SECTION_508_COMPLIANCE.md", "SECTION_508_COMPLIANCE.md"),
            (self.root_dir / "sample_data.csv", "sample_data.csv"),
        ]
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for src, dst in files_to_include:
                if src.exists():
                    zf.write(src, dst)
                    print(f"  Added: {dst}")
        
        size_mb = zip_path.stat().st_size / (1024 * 1024)
        print(f"\nPortable ZIP created: {zip_path}")
        print(f"Size: {size_mb:.1f} MB")
        return True
    
    def build_all(self):
        """Build everything."""
        print("=" * 60)
        print(f"CiviQual Stats {self.app_version} - Complete Build")
        print("=" * 60)
        
        self.clean()
        
        if not self.build_executable():
            return False
        
        if not self.build_installer():
            print("\nInstaller build skipped (Inno Setup not found)")
        
        if not self.create_portable_zip():
            return False
        
        print("\n" + "=" * 60)
        print("BUILD COMPLETE")
        print("=" * 60)
        print(f"\nOutput files in: {self.dist_dir}")
        print(f"Installer in: {self.output_dir}")
        
        return True


def main():
    """Main entry point."""
    builder = CiviQualStatsInstallerBuilder()
    
    if len(sys.argv) < 2:
        print("Usage: python build_installer.py <command>")
        print("\nCommands:")
        print("  clean     - Remove build artifacts")
        print("  icon      - Generate Windows icon")
        print("  exe       - Build executable only")
        print("  installer - Build installer (requires exe)")
        print("  portable  - Create portable ZIP")
        print("  all       - Build everything")
        return 1
    
    command = sys.argv[1].lower()
    
    if command == "clean":
        builder.clean()
    elif command == "icon":
        builder.create_icon()
    elif command == "exe":
        if not builder.build_executable():
            return 1
    elif command == "installer":
        if not builder.build_installer():
            return 1
    elif command == "portable":
        if not builder.create_portable_zip():
            return 1
    elif command == "all":
        if not builder.build_all():
            return 1
    else:
        print(f"Unknown command: {command}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
