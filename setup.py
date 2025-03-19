from setuptools import find_packages, setup

setup(
    name="pyerp",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "django>=5.1.6",
    ],
)
