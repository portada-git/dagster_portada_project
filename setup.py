from setuptools import find_packages, setup

setup(
    name="dagster_portada_project",
    version="0.0.2",
    description='....... for PortADa project',
    author='PortADa team',
    author_email='jcbportada@gmail.com',
    license='MIT',
    packages=find_packages(exclude=["dagster_portada_project_tests"]),
    install_requires=[
        "dagster"
    ],
    extras_require={"dev": ["dagster-webserver", "pytest"]},
)
