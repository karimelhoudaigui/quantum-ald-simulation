from setuptools import find_packages, setup

setup(
    name="quantum-ald-simulation",
    version="0.1.0",
    author="Karim El Houdaigui",
    description="Hybrid quantum-classical simulation for ALD reactions",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/karimelhoudaigui/quantum-ald-simulation",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
)
