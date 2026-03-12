from setuptools import setup, find_packages

setup(
    name="aegisnet-python",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "httpx>=0.20.0",
    ],
    author="Varun",
    description="AegisNet Python SDK — Secure AI Infrastructure",
)
