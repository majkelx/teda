"""Desktop entry installation for Linux systems"""
import os
import sys
import shutil
import subprocess
from pathlib import Path


def is_linux():
    """Check if running on Linux"""
    return sys.platform.startswith('linux')


def get_assets_dir():
    """Get the assets directory path"""
    # When installed via pip, assets should be in package data
    package_dir = Path(__file__).parent.parent
    assets_dir = package_dir / 'assets'

    if not assets_dir.exists():
        # Fallback to development structure
        assets_dir = Path(__file__).parent.parent / 'assets'

    return assets_dir


def install_desktop_entry():
    """Install desktop entry and icon for Linux"""
    if not is_linux():
        print("Desktop entry installation is only supported on Linux.")
        print("Current platform:", sys.platform)
        return False

    try:
        assets_dir = get_assets_dir()

        # Paths
        icon_src = assets_dir / 'teda.svg'
        desktop_src = assets_dir / 'teda.desktop'

        if not icon_src.exists():
            print(f"Error: Icon file not found at {icon_src}")
            return False

        if not desktop_src.exists():
            print(f"Error: Desktop file not found at {desktop_src}")
            return False

        # Target directories
        home = Path.home()
        icon_dir = home / '.local' / 'share' / 'icons' / 'hicolor' / 'scalable' / 'apps'
        desktop_dir = home / '.local' / 'share' / 'applications'

        # Create directories if they don't exist
        icon_dir.mkdir(parents=True, exist_ok=True)
        desktop_dir.mkdir(parents=True, exist_ok=True)

        # Copy files
        icon_dest = icon_dir / 'teda.svg'
        desktop_dest = desktop_dir / 'teda.desktop'

        print(f"Copying {icon_src} -> {icon_dest}")
        shutil.copy2(icon_src, icon_dest)

        print(f"Copying {desktop_src} -> {desktop_dest}")
        shutil.copy2(desktop_src, desktop_dest)

        # Make desktop file executable
        os.chmod(desktop_dest, 0o755)

        # Update desktop database
        try:
            print("Updating desktop database...")
            subprocess.run(['update-desktop-database', str(desktop_dir)],
                         check=False, capture_output=True)
        except FileNotFoundError:
            print("update-desktop-database not found, skipping...")

        # Update icon cache
        try:
            print("Updating icon cache...")
            icon_base = home / '.local' / 'share' / 'icons' / 'hicolor'
            subprocess.run(['gtk-update-icon-cache', '-f', '-t', str(icon_base)],
                         check=False, capture_output=True)
        except FileNotFoundError:
            print("gtk-update-icon-cache not found, skipping...")

        print("\n✓ TeDa desktop entry installed successfully!")
        print(f"  Icon: {icon_dest}")
        print(f"  Desktop entry: {desktop_dest}")
        print("\nTeDa should now appear in your application menu.")
        print("You may need to log out and log back in for changes to take effect.")

        # Ubuntu-specific: try to add to favorites
        try_add_to_favorites()

        return True

    except Exception as e:
        print(f"Error installing desktop entry: {e}")
        import traceback
        traceback.print_exc()
        return False


def uninstall_desktop_entry():
    """Uninstall desktop entry and icon"""
    if not is_linux():
        print("Desktop entry uninstallation is only supported on Linux.")
        return False

    try:
        home = Path.home()
        icon_path = home / '.local' / 'share' / 'icons' / 'hicolor' / 'scalable' / 'apps' / 'teda.svg'
        desktop_path = home / '.local' / 'share' / 'applications' / 'teda.desktop'

        removed = False

        if icon_path.exists():
            print(f"Removing {icon_path}")
            icon_path.unlink()
            removed = True

        if desktop_path.exists():
            print(f"Removing {desktop_path}")
            desktop_path.unlink()
            removed = True

        if not removed:
            print("No desktop entry or icon found to remove.")
            return True

        # Update desktop database
        try:
            desktop_dir = home / '.local' / 'share' / 'applications'
            subprocess.run(['update-desktop-database', str(desktop_dir)],
                         check=False, capture_output=True)
        except FileNotFoundError:
            pass

        # Update icon cache
        try:
            icon_base = home / '.local' / 'share' / 'icons' / 'hicolor'
            subprocess.run(['gtk-update-icon-cache', '-f', '-t', str(icon_base)],
                         check=False, capture_output=True)
        except FileNotFoundError:
            pass

        print("\n✓ TeDa desktop entry uninstalled successfully!")
        return True

    except Exception as e:
        print(f"Error uninstalling desktop entry: {e}")
        return False


def try_add_to_favorites():
    """Try to add TeDa to favorites in Ubuntu (GNOME)"""
    try:
        # Check if we're on GNOME
        if 'GNOME' not in os.environ.get('XDG_CURRENT_DESKTOP', ''):
            return

        # Use gsettings to add to favorites
        result = subprocess.run(
            ['gsettings', 'get', 'org.gnome.shell', 'favorite-apps'],
            capture_output=True, text=True, check=False
        )

        if result.returncode != 0:
            return

        current_favorites = result.stdout.strip()

        # Check if teda.desktop is already in favorites
        if 'teda.desktop' in current_favorites:
            return

        # Parse current favorites (it's a list like: ['firefox.desktop', 'thunderbird.desktop'])
        import ast
        try:
            favorites_list = ast.literal_eval(current_favorites)
        except:
            return

        # Add teda.desktop
        favorites_list.append('teda.desktop')
        new_favorites = str(favorites_list)

        subprocess.run(
            ['gsettings', 'set', 'org.gnome.shell', 'favorite-apps', new_favorites],
            check=False, capture_output=True
        )

        print("\n✓ TeDa added to favorites panel (GNOME/Ubuntu)")

    except Exception:
        # Silently fail - this is optional
        pass
