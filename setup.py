"""
Setup script for Market Regime Detection System
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="market-regime-detection",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Market Regime Detection System for Indian Stock Market",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/market-regime-detection",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=[
        "numpy>=1.24.3",
        "pandas>=2.0.3",
        "scikit-learn>=1.3.0",
        "scipy>=1.11.1",
        "yfinance>=0.2.28",
        "hmmlearn>=0.3.0",
        "plotly>=5.16.1",
        "streamlit>=1.26.0",
    ],
)
