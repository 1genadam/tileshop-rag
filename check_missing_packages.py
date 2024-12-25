import subprocess

def get_installed_packages():
    """Get a set of installed packages using pip list."""
    result = subprocess.run(["pip", "list", "--format=freeze"], capture_output=True, text=True)
    installed = {line.split("==")[0] for line in result.stdout.splitlines() if "==" in line}
    return installed

def get_required_packages(requirements_file="requirements.txt"):
    """Get a set of required packages from requirements.txt."""
    try:
        with open(requirements_file, "r") as file:
            required = {line.split("==")[0] for line in file.read().splitlines() if "==" in line}
        return required
    except FileNotFoundError:
        print(f"Error: {requirements_file} not found.")
        return set()

def find_missing_packages(installed, required):
    """Find missing packages."""
    return required - installed

if __name__ == "__main__":
    installed_packages = get_installed_packages()
    required_packages = get_required_packages()

    if not required_packages:
        print("No required packages found in requirements.txt.")
    else:
        missing_packages = find_missing_packages(installed_packages, required_packages)
        if missing_packages:
            print("Missing packages:")
            for package in missing_packages:
                print(f"- {package}")
        else:
            print("All required packages are installed.")

