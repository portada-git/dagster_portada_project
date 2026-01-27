from setuptools import find_packages, setup

setup(
    author='PortADa team',
    author_email='jcbportada@gmail.com',
    license='MIT',
    packages=find_packages(exclude=["dagster_portada_project_tests"]),
    install_requires=[
        "dagster",
        "py_portada_data_layer @ git+https://github.com/portada-git/py_portada_data_layer",
    ],
    extras_require={"dev": ["dagster-webserver", "pytest"]},
)
