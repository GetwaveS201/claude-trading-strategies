"""
Setup script for backtester package
"""

from setuptools import setup, find_packages

setup(
    name="backtester",
    version="1.0.0",
    description="Professional stock backtesting engine",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.3.0",
        "numpy>=1.21.0",
        "matplotlib>=3.4.0",
        "pytest>=7.0.0",
    ],
    entry_points={
        "console_scripts": [
            "backtester=backtester.cli:main",
        ],
    },
)
