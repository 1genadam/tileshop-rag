import pkg_resources

def list_dependencies(requirements_file):
    """
    Parse the requirements.txt file and identify which libraries depend on numpy.

    :param requirements_file: Path to the requirements.txt file.
    :return: List of packages requiring numpy.
    """
    dependencies = {}
    
    try:
        with open(requirements_file, 'r') as f:
            packages = [line.strip() for line in f if line.strip() and not line.startswith('#')]

        for package in packages:
            try:
                dist = pkg_resources.require(package)
                dependencies[package] = [req.project_name for req in dist[0].requires()]
            except Exception as e:
                dependencies[package] = f"Error parsing package: {e}"

        numpy_dependents = {pkg: deps for pkg, deps in dependencies.items() if 'numpy' in deps}
        return numpy_dependents
    except FileNotFoundError:
        return "Requirements file not found."

# Example usage:
if __name__ == "__main__":
    requirements_path = "requirements.txt"
    numpy_deps = list_dependencies(requirements_path)
    print("Packages requiring numpy:", numpy_deps)

