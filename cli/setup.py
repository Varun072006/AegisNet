from setuptools import setup

setup(
    name="aegisnet-cli",
    version="0.1.0",
    py_modules=["aegis"],
    install_requires=[
        "click",
        "requests",
    ],
    entry_points={
        "console_scripts": [
            "aegis=aegis:cli",
        ],
    },
)
