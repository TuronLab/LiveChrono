from setuptools import setup

# Read the long description from README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="live-chrono",
    version="0.1.0",
    author="Pablo Turon",
    author_email="ptmallor@gmail.com",
    description="Live-updating elapsed timer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/turonlab/live-chrono",
    python_requires=">=3.7",
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Utilities",
    ],
    keywords="timer live elapsed progress",
    # List the three .py files here, without the .py extension:
    py_modules=["live_chrono", "utils", "model"],
)
