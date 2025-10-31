from setuptools import setup, find_packages

setup(
    name="pomodoro-timer",
    version="1.0.0",
    description="A modern Pomodoro timer application with GUI",
    long_description=open("resources/docs/README.md").read(),
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={
        "pomodoro_timer": ["../resources/sounds/*.wav"],
    },
    install_requires=[
        "pygame>=2.6.0",
        "pyinstaller>=5.0",
    ],
    entry_points={
        "console_scripts": [
            "pomodoro-timer=pomodoro_timer.pomodoro:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    python_requires=">=3.8",
)
