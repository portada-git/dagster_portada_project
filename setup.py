from setuptools import find_packages, setup

setup(
    name="dagster_portada_project",
    packages=find_packages(exclude=["dagster_portada_project_tests"]),
    install_requires=[
        "dagster",
        "dagster_graphql",
        "watchdog"
    ],
    #extras_require={"dev": ["dagster-webserver", "pytest"]},
)
