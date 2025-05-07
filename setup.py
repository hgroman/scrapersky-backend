"""
ScraperSky setup configuration
"""

from setuptools import find_packages, setup

setup(
    name="scrapersky",
    version="0.1.0",
    description="ScraperSky Backend",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "sqlalchemy>=2.0.0",
        "pydantic>=2.0.0",
        "asyncpg",
        "python-jose",
    ],
    python_requires=">=3.8",
)
