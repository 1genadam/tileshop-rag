from setuptools import setup, find_packages

setup(
    name="anchor_guardian",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        'watchdog>=3.0.0',
        'python-dotenv>=1.0.0'
    ],
    entry_points={
        'console_scripts': [
            'anchor-monitor=anchor_guardian.integrations.avatar_monitor:main',
        ],
    }
)
