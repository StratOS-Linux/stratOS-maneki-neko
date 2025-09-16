#!/usr/bin/env python3
"""
Package Installer Orchestrator
Manages the installation of AUR and Pacman packages with proper privilege handling.
"""

import subprocess
import sys
import os
import threading
import time
import json
import argparse
from typing import List, Dict, Any


class PackageInstaller:
    def __init__(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.aur_builder_script = os.path.join(self.script_dir, "aurPackageBuilder.sh")
        self.aur_installer_script = os.path.join(self.script_dir, "aurPackageInstaller.sh")
        self.pacman_installer_script = os.path.join(self.script_dir, "pacmanPackageInstaller.sh")
        self.flatpak_installer_script = os.path.join(self.script_dir, "flatpakPackageInstaller.sh")
        
        self.progress = {
            'aur_builder': {'status': 'pending', 'progress': 0, 'message': ''},
            'aur_installer': {'status': 'pending', 'progress': 0, 'message': ''},
            'pacman_installer': {'status': 'pending', 'progress': 0, 'message': ''},
            'flatpak_installer': {'status': 'pending', 'progress': 0, 'message': ''}
        }
        
        self.lock = threading.Lock()

    def print_progress(self):
        """Print the current installation progress in a CLI format."""
        os.system('clear')  # Clear terminal
        print("=" * 60)
        print("📦 PACKAGE INSTALLATION PROGRESS")
        print("=" * 60)
        
        for stage, info in self.progress.items():
            status_icon = {
                'pending': '⏳',
                'running': '🔄',
                'completed': '✅',
                'failed': '❌'
            }.get(info['status'], '❓')
            
            stage_name = {
                'aur_builder': 'AUR Package Builder',
                'aur_installer': 'AUR Package Installer',
                'pacman_installer': 'Pacman Package Installer',
                'flatpak_installer': 'Flatpak Package Installer'
            }.get(stage, stage)
            
            progress_bar = self.create_progress_bar(info['progress'])
            print(f"{status_icon} {stage_name:.<30} {progress_bar} {info['progress']:>3}%")
            
            if info['message']:
                print(f"   └─ {info['message']}")
        
        print("=" * 60)

    def create_progress_bar(self, progress: int, width: int = 20) -> str:
        """Create a visual progress bar."""
        filled = int(width * progress / 100)
        bar = '█' * filled + '░' * (width - filled)
        return f"[{bar}]"

    def update_progress(self, stage: str, status: str, progress: int = 0, message: str = ""):
        """Update progress for a specific stage."""
        with self.lock:
            self.progress[stage]['status'] = status
            self.progress[stage]['progress'] = progress
            self.progress[stage]['message'] = message
        self.print_progress()

    def run_script_as_user(self, script_path: str, packages: List[str], stage: str) -> bool:
        """Run a bash script as the current user (non-root)."""
        try:
            self.update_progress(stage, 'running', 0, f"Starting {os.path.basename(script_path)}")
            
            # Run bash script with package arguments
            cmd = ['bash', script_path] + packages
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Monitor progress and capture output in real-time
            progress = 0
            total_packages = len(packages)
            packages_processed = 0
            
            for line in iter(process.stdout.readline, ''):
                line = line.strip()
                if line:
                    # Update progress based on script output
                    if '[OK]' in line and 'built successfully' in line:
                        packages_processed += 1
                        progress = int((packages_processed / total_packages) * 100)
                        self.update_progress(stage, 'running', progress, f"Built {packages_processed}/{total_packages} packages")
                    elif '[ERROR]' in line:
                        self.update_progress(stage, 'running', progress, f"Error: {line[:50]}...")
                    elif '==>' in line:
                        self.update_progress(stage, 'running', progress, line[:50])
            
            process.wait()
            
            if process.returncode == 0:
                self.update_progress(stage, 'completed', 100, "Build completed successfully")
                return True
            else:
                self.update_progress(stage, 'failed', progress, "Build failed")
                return False
                
        except Exception as e:
            self.update_progress(stage, 'failed', 0, f"Error: {str(e)[:50]}...")
            return False

    def run_script_as_root_with_exit_code(self, script_path: str, packages: List[str], stage: str, extra_args: List[str] = None, auth_method: str = 'pkexec') -> tuple[bool, int]:
        """Run a bash script as root and return both success status and exit code."""
        try:
            script_name = os.path.basename(script_path)
            
            # Show authentication prompt for root operations
            if auth_method == 'pkexec':
                print(f"\n🔐 Authentication Required for {script_name}")
                print("   Please authenticate as superuser when prompted...")
                time.sleep(2)  # Give user time to read the message
            
            self.update_progress(stage, 'running', 0, f"Starting {script_name} (requesting authentication)")
            
            # Build command based on auth method
            if auth_method == 'sudo':
                cmd = ['sudo', 'bash', script_path]
            else:
                cmd = ['pkexec', 'bash', script_path]
            
            if extra_args:
                cmd.extend(extra_args)
            cmd.extend(packages)
            
            # Start the process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Monitor authentication and progress
            progress = 0
            total_packages = len(packages)
            packages_processed = 0
            auth_timeout = 10
            auth_start_time = time.time()
            auth_completed = False
            
            for line in iter(process.stdout.readline, ''):
                line = line.strip()
                if line:
                    # Check for authentication completion
                    if not auth_completed and ('==> ' in line or 'Installing' in line or '[OK]' in line):
                        auth_completed = True
                        self.update_progress(stage, 'running', 5, "Authentication successful, processing...")
                    
                    # Check for authentication timeout
                    if not auth_completed and (time.time() - auth_start_time) > auth_timeout:
                        print(f"\n⏰ Authentication timeout after {auth_timeout} seconds.")
                        process.terminate()
                        
                        # Offer sudo fallback
                        if auth_method == 'pkexec':
                            response = input("Would you like to use sudo instead of pkexec? (y/n): ").lower().strip()
                            if response in ['y', 'yes']:
                                print("🔄 Retrying with sudo...")
                                return self.run_script_as_root_with_exit_code(script_path, packages, stage, extra_args, 'sudo')
                        
                        self.update_progress(stage, 'failed', 0, "Authentication failed or timed out")
                        return False, 127  # Authentication failure exit code
                    
                    # Update progress based on script output
                    if '[OK]' in line and ('installed successfully' in line or 'built successfully' in line):
                        packages_processed += 1
                        progress = int((packages_processed / total_packages) * 100)
                        if 'installer' in stage:
                            self.update_progress(stage, 'running', progress, f"Installed {packages_processed}/{total_packages} packages")
                        else:
                            self.update_progress(stage, 'running', progress, f"Processed {packages_processed}/{total_packages} packages")
                    elif '[ERROR]' in line:
                        self.update_progress(stage, 'running', progress, f"Error: {line[:50]}...")
                    elif '==> ' in line:
                        # Extract meaningful progress messages
                        if 'Installing' in line or 'Starting' in line or 'Syncing' in line:
                            self.update_progress(stage, 'running', progress, line[:50])
                    elif progress_char := ('*' if '*' in line else '#' if '#' in line else None):
                        # Count progress characters to estimate progress
                        char_count = line.count(progress_char)
                        if char_count > 0:
                            progress = min(progress + (char_count * 2), 90)  # Increment based on progress chars
                            self.update_progress(stage, 'running', progress, "Processing...")
            
            process.wait()
            exit_code = process.returncode
            
            if exit_code == 0:
                self.update_progress(stage, 'completed', 100, "Installation completed successfully")
                return True, exit_code
            elif exit_code == 127:
                self.update_progress(stage, 'failed', progress, "Authentication failed")
                return False, exit_code
            else:
                self.update_progress(stage, 'failed', progress, f"Installation failed (exit code: {exit_code})")
                return False, exit_code
                
        except Exception as e:
            self.update_progress(stage, 'failed', 0, f"Error: {str(e)[:50]}...")
            return False, -1

    def run_script_as_root(self, script_path: str, packages: List[str], stage: str, extra_args: List[str] = None, auth_method: str = 'pkexec') -> bool:
        """Run a bash script as root using pkexec or sudo with authentication handling."""
        result, exit_code = self.run_script_as_root_with_exit_code(script_path, packages, stage, extra_args, auth_method)
        
        # Handle authentication failure for individual script calls
        if not result and exit_code == 127:
            print(f"\n⚠️  Authentication failed for {os.path.basename(script_path)}")
            retry_response = input("Would you like to retry authentication? (y/n): ").lower().strip()
            
            if retry_response in ['y', 'yes']:
                print("🔄 Retrying authentication...")
                result, _ = self.run_script_as_root_with_exit_code(script_path, packages, stage, extra_args, auth_method)
        
        return result

    def authenticate_with_timeout(self, message: str, timeout: int = 10) -> str:
        """Show authentication prompt and wait for timeout, return chosen auth method."""
        print(f"\n🔐 {message}")
        print(f"⏰ Waiting {timeout} seconds for authentication...")
        print("   If authentication fails or times out, you'll be given option to use sudo instead.")
        
        import threading
        import time
        
        auth_completed = threading.Event()
        
        def timeout_handler():
            time.sleep(timeout)
            if not auth_completed.is_set():
                print(f"\n⏰ Authentication timeout after {timeout} seconds.")
                response = input("Would you like to use sudo instead of pkexec? (y/n): ").lower().strip()
                if response.lower() in ['y', 'yes']:
                    auth_completed.set()
                    return 'sudo'
                
                else:
                    print("❌ Authentication cancelled by user.")
                    auth_completed.set()
                    return 'cancelled'
        
        timeout_thread = threading.Thread(target=timeout_handler)
        timeout_thread.daemon = True
        timeout_thread.start()
        
        return 'pkexec'  # Default to pkexec initially

    def handle_auth_failure_retry(self, failed_scripts: List[Dict[str, Any]]) -> bool:
        """Handle authentication failure by offering retry option to user."""
        if not failed_scripts:
            return True
        
        print("\n" + "=" * 60)
        print("🔐 AUTHENTICATION FAILURE DETECTED")
        print("=" * 60)
        print("The following operations failed due to authentication issues:")
        
        for script in failed_scripts:
            script_name = os.path.basename(script['script_path'])
            print(f"   ❌ {script_name} - {len(script['packages'])} packages")
        
        print("\nWould you like to retry these operations?")
        print("This will give you another chance to authenticate as root.")
        
        retry_response = input("Retry authentication? (y/n): ").lower().strip()
        
        if retry_response in ['y', 'yes']:
            print("\n🔄 Retrying failed operations...")
            return self.run_parallel_scripts(failed_scripts)
        else:
            print("❌ Skipping retry. Some packages may not be installed.")
            return False

    def run_parallel_scripts(self, script_configs: List[Dict[str, Any]]) -> bool:
        """Run multiple scripts in parallel using threading."""
        import concurrent.futures
        
        results = []
        failed_auth_scripts = []
        
        def run_single_script(config):
            script_path = config['script_path']
            packages = config['packages']
            stage = config['stage']
            auth_method = config.get('auth_method', 'user')
            extra_args = config.get('extra_args', [])
            
            if auth_method == 'user':
                return self.run_script_as_user(script_path, packages, stage)
            else:
                result, exit_code = self.run_script_as_root_with_exit_code(script_path, packages, stage, extra_args, auth_method)
                # Check for authentication failure (exit code 127)
                if not result and exit_code == 127:
                    failed_auth_scripts.append(config)
                return result
        
        # Use ThreadPoolExecutor to run scripts in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(script_configs)) as executor:
            # Submit all tasks
            future_to_config = {executor.submit(run_single_script, config): config for config in script_configs}
            
            # Wait for all to complete
            for future in concurrent.futures.as_completed(future_to_config):
                config = future_to_config[future]
                try:
                    result = future.result()
                    results.append((config['stage'], result))
                except Exception as e:
                    print(f"❌ Error in {config['stage']}: {e}")
                    results.append((config['stage'], False))
        
        # Check if any scripts failed due to authentication
        if failed_auth_scripts:
            print(f"\n⚠️  {len(failed_auth_scripts)} operations failed due to authentication issues.")
            if self.handle_auth_failure_retry(failed_auth_scripts):
                # Update results for retried scripts
                for script in failed_auth_scripts:
                    for i, (stage, _) in enumerate(results):
                        if stage == script['stage']:
                            results[i] = (stage, True)
                            break
        
        # Return True only if all scripts succeeded
        return all(result for _, result in results)

    def install_packages(self, aur_packages: List[str], pacman_packages: List[str], flatpak_packages: List[str] = None, 
                        install_flatpak_system_wide: bool = False, yankrepos: bool = False) -> bool:
        """
        Main installation orchestrator.
        Handles AUR, Pacman, and Flatpak package installation with optimal parallel processing.
        """
        success = True
        
        # Ensure flatpak_packages is a list
        if flatpak_packages is None:
            flatpak_packages = []
        
        print(f"📋 Installation Summary:")
        print(f"   🔧 AUR packages: {len(aur_packages)} - {aur_packages}")
        print(f"   � Pacman packages: {len(pacman_packages)} - {pacman_packages}")
        print(f"   📱 Flatpak packages: {len(flatpak_packages)} - {flatpak_packages}")
        print(f"   🌐 Flatpak scope: {'system-wide' if install_flatpak_system_wide else 'user-only'}")
        print()
        
        # Phase 1: Non-root operations that can run in parallel
        phase1_scripts = []
        
        if aur_packages:
            print(f"🔧 Phase 1: AUR package building (non-root)")
            phase1_scripts.append({
                'script_path': self.aur_builder_script,
                'packages': aur_packages,
                'stage': 'aur_builder',
                'auth_method': 'user'
            })
        else:
            self.update_progress('aur_builder', 'completed', 100, "No AUR packages to build")
        
        # Add flatpak installation to Phase 1 if user-only installation
        if flatpak_packages and not install_flatpak_system_wide:
            print(f"📱 Phase 1: Flatpak package installation (user-only, parallel with AUR building)")
            phase1_scripts.append({
                'script_path': self.flatpak_installer_script,
                'packages': flatpak_packages,
                'stage': 'flatpak_installer',
                'auth_method': 'user'
            })
        elif not flatpak_packages:
            self.update_progress('flatpak_installer', 'completed', 100, "No Flatpak packages to install")
        
        # Execute Phase 1 scripts in parallel
        if phase1_scripts:
            print(f"🚀 Executing {len(phase1_scripts)} operations in parallel...")
            if not self.run_parallel_scripts(phase1_scripts):
                print("❌ Phase 1 failed!")
                return False
        
        # Phase 2: Sequential execution of pacman-based operations (AUR installer → Pacman installer)
        # with optional parallel flatpak system-wide installation
        
        if aur_packages or pacman_packages or (flatpak_packages and install_flatpak_system_wide):
            print(f"🔧 Phase 2: Root-level installations with proper sequencing")
            
            # Step 2.1: AUR package installation (uses pacman, must be first)
            if aur_packages:
                print(f"🔧 Step 2.1: Installing AUR packages (uses pacman)")
                
                # Prepare scripts for potential parallel execution
                aur_install_scripts = [{
                    'script_path': self.aur_installer_script,
                    'packages': aur_packages,
                    'stage': 'aur_installer',
                    'auth_method': 'pkexec'
                }]
                
                # Add system-wide flatpak installation in parallel if requested
                if flatpak_packages and install_flatpak_system_wide:
                    print(f"📱 Step 2.1: Installing Flatpaks system-wide (parallel with AUR)")
                    aur_install_scripts.append({
                        'script_path': self.flatpak_installer_script,
                        'packages': flatpak_packages,
                        'stage': 'flatpak_installer',
                        'auth_method': 'pkexec'
                    })
                
                # Execute AUR installation (and optionally flatpak system-wide in parallel)
                if not self.run_parallel_scripts(aur_install_scripts):
                    print("❌ AUR package installation failed!")
                    success = False
                    # Continue to pacman installation even if AUR failed
            else:
                self.update_progress('aur_installer', 'completed', 100, "No AUR packages to install")
                
                # If no AUR packages but system-wide flatpak requested, install it separately
                if flatpak_packages and install_flatpak_system_wide:
                    print(f"📱 Step 2.1: Installing Flatpaks system-wide (standalone)")
                    if not self.run_script_as_root(self.flatpak_installer_script, flatpak_packages, 'flatpak_installer'):
                        print("❌ Flatpak system-wide installation failed!")
                        success = False
            
            # Step 2.2: Pacman package installation (uses pacman, must be after AUR)
            if pacman_packages:
                print(f"📦 Step 2.2: Installing Pacman packages (sequential after AUR)")
                
                extra_args = ['--yankrepos'] if yankrepos else []
                if not self.run_script_as_root(self.pacman_installer_script, pacman_packages, 'pacman_installer', extra_args):
                    print("❌ Pacman package installation failed!")
                    success = False
            else:
                self.update_progress('pacman_installer', 'completed', 100, "No Pacman packages to install")
        
        return success
        
        
        # Phase 2: Root-level installations (can run in parallel if no conflicts)
        phase2_scripts = []
        
        if aur_packages:
            print(f"� Phase 2: AUR package installation (root)")
            phase2_scripts.append({
                'script_path': self.aur_installer_script,
                'packages': aur_packages,
                'stage': 'aur_installer',
                'auth_method': 'pkexec'
            })
        else:
            self.update_progress('aur_installer', 'completed', 100, "No AUR packages to install")
        
        if pacman_packages:
            print(f"📦 Phase 2: Pacman package installation (root)")
            extra_args = ['--yankrepos'] if yankrepos else []
            phase2_scripts.append({
                'script_path': self.pacman_installer_script,
                'packages': pacman_packages,
                'stage': 'pacman_installer',
                'auth_method': 'pkexec',
                'extra_args': extra_args
            })
        else:
            self.update_progress('pacman_installer', 'completed', 100, "No Pacman packages to install")
        
        # Add flatpak installation to Phase 2 if system-wide installation
        if flatpak_packages and install_flatpak_system_wide:
            print(f"📱 Phase 2: Flatpak package installation (system-wide, parallel with other root operations)")
            phase2_scripts.append({
                'script_path': self.flatpak_installer_script,
                'packages': flatpak_packages,
                'stage': 'flatpak_installer',
                'auth_method': 'pkexec'
            })
        
        # Execute Phase 2 scripts in parallel
        if phase2_scripts:
            print(f"🚀 Executing {len(phase2_scripts)} root operations in parallel...")
            if not self.run_parallel_scripts(phase2_scripts):
                print("❌ Phase 2 failed!")
                success = False
        
        return success

    def parse_arguments(self):
        """Parse command line arguments."""
        parser = argparse.ArgumentParser(description='Package Installation Orchestrator')
        
        # Method 1: JSON string arguments
        parser.add_argument('--aur-json', type=str, help='JSON string of AUR packages list')
        parser.add_argument('--pacman-json', type=str, help='JSON string of Pacman packages list')
        parser.add_argument('--flatpak-json', type=str, help='JSON string of Flatpak packages list')
        
        # Method 2: Individual package arguments
        parser.add_argument('--aur', nargs='*', default=[], help='List of AUR packages')
        parser.add_argument('--pacman', nargs='*', default=[], help='List of Pacman packages')
        parser.add_argument('--flatpak', nargs='*', default=[], help='List of Flatpak packages')
        
        # Method 3: Combined JSON argument
        parser.add_argument('--packages-json', type=str, help='JSON string with aur, pacman, and flatpak package lists')
        
        # Installation options
        parser.add_argument('--yankrepos', action='store_true', 
                          help='Sync package databases before installing pacman packages')
        parser.add_argument('--install-flatpak-system-wide', '--installFlatpaksSystemWide', '--ifsw', 
                          action='store_true',
                          help='Install flatpak packages system-wide (requires root)')
        
        return parser.parse_args()

    def main(self):
        """Main entry point for the package installer."""
        print("🚀 Starting package installation orchestrator...")
        
        args = self.parse_arguments()
        
        # Parse package lists from arguments
        aur_packages = []
        pacman_packages = []
        flatpak_packages = []
        
        # Method 1: JSON string arguments
        if args.aur_json:
            try:
                aur_packages = json.loads(args.aur_json)
            except json.JSONDecodeError:
                print("❌ Invalid JSON format for AUR packages")
                return 1
        
        if args.pacman_json:
            try:
                pacman_packages = json.loads(args.pacman_json)
            except json.JSONDecodeError:
                print("❌ Invalid JSON format for Pacman packages")
                return 1
        
        if args.flatpak_json:
            try:
                flatpak_packages = json.loads(args.flatpak_json)
            except json.JSONDecodeError:
                print("❌ Invalid JSON format for Flatpak packages")
                return 1
        
        # Method 2: Individual package arguments (override JSON if provided)
        if args.aur:
            aur_packages = args.aur
        
        if args.pacman:
            pacman_packages = args.pacman
        
        if args.flatpak:
            flatpak_packages = args.flatpak
        
        # Method 3: Combined JSON argument (takes precedence)
        if args.packages_json:
            try:
                package_data = json.loads(args.packages_json)
                aur_packages = package_data.get('aur', [])
                pacman_packages = package_data.get('pacman', [])
                flatpak_packages = package_data.get('flatpak', [])
            except json.JSONDecodeError:
                print("❌ Invalid JSON format for combined packages")
                return 1
        
        # Validate that we have at least one package to install
        if not aur_packages and not pacman_packages and not flatpak_packages:
            print("❌ No packages specified for installation")
            print("Usage examples:")
            print("  python3 package_installer.py --aur yay brave-bin --pacman git vim --flatpak com.spotify.Client")
            print("  python3 package_installer.py --packages-json '{\"aur\":[\"yay\"],\"pacman\":[\"git\"],\"flatpak\":[\"com.spotify.Client\"]}'")
            return 1
        
        print(f"📋 AUR packages: {aur_packages}")
        print(f"📋 Pacman packages: {pacman_packages}")
        print(f"📋 Flatpak packages: {flatpak_packages}")
        print()
        
        # Initialize progress display
        self.print_progress()
        
        # Start installation process
        success = self.install_packages(aur_packages, pacman_packages, flatpak_packages, 
                                      args.install_flatpak_system_wide, args.yankrepos)
        
        # Final status
        print("\n" + "=" * 60)
        if success:
            print("🎉 All packages installed successfully!")
        else:
            print("💥 Package installation completed with errors!")
        print("=" * 60)
        
        input("Press Enter to close...")  # Keep terminal open
        
        return 0 if success else 1


if __name__ == "__main__":
    installer = PackageInstaller()
    exit_code = installer.main()
    sys.exit(exit_code)