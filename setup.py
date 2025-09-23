from setuptools import setup

# Read the long description from README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="live-chrono",
    version="1.0.0",
    author="Pablo Turon",
    author_email="ptmallor@gmail.com",
    description="Live-updating elapsed timer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TuronLab/LiveChrono",
    python_requires=">=3.7",
    include_package_data=True,
    install_requires=[],
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Utilities",
    ],
    keywords="timer live elapsed progress chrono",
    packages=["live_chrono"],
)
