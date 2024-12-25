import subprocess

def install_missing_and_outdated(file_path):
    with open(file_path, "r") as f:
        required_packages = [line.strip() for line in f if "==" in line]

    for pkg in required_packages:
        try:
            subprocess.run(f"pip install {pkg}", shell=True, check=True)
            print(f"Installed: {pkg}")
        except subprocess.CalledProcessError:
            print(f"Failed to install: {pkg}")

if __name__ == "__main__":
    install_missing_and_outdated("requirements_latest.txt")

