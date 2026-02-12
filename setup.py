from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="hawkeye-recon",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Automated Reconnaissance Framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/hawkeye",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Information Technology",
        "Topic :: Security",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pyyaml>=6.0",
        "requests>=2.31.0",
        "rich>=13.7.0",
        "colorama>=0.4.6",
    ],
    entry_points={
        "console_scripts": [
            "hawkeye=hawkeye.cli:main",
        ],
    },
    include_package_data=True,
)
