from setuptools import setup, find_packages

setup(
    name="m4_pytestDoc",
    version="25.10",
    packages=find_packages(),
    install_requires=[
        'flask',
        'psycopg',
        'psycopg-pool',
        'beautifulsoup4',
        'urllib3',
        'sphinx'
    ],
)