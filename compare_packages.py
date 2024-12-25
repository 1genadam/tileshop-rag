import pkg_resources

def get_installed_packages():
    return {pkg.key: pkg.version for pkg in pkg_resources.working_set}

def get_required_packages():
    with open("requirements.txt") as f:
        return dict(line.strip().split("==") for line in f if "==" in line)

installed = get_installed_packages()
required = get_required_packages()

missing = {pkg: ver for pkg, ver in required.items() if pkg not in installed}
incorrect_version = {pkg: (installed[pkg], ver) for pkg, ver in required.items() if pkg in installed and installed[pkg] != ver}

print("\nMissing Packages:")
for pkg, ver in missing.items():
    print(f"{pkg}=={ver}")

print("\nIncorrect Versions:")
for pkg, (installed_ver, required_ver) in incorrect_version.items():
    print(f"{pkg}: Installed={installed_ver}, Required={required_ver}")

