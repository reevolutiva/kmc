from setuptools import setup, find_packages

setup(
    name="kmc-parser",
    version="0.1.0",
    description="Kimfe Markdown Convention Parser - Un parser para plantillas inteligentes con LLMs",
    author="Kimfe Team",
    author_email="info@kimfe.com",
    url="https://kimfe.com",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    install_requires=[
        "regex>=2022.1.18",
        "llama-index>=0.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.1.0",
            "isort>=5.10.1",
            "mypy>=0.941",
        ],
        "langchain": [
            "langchain>=0.0.200",
        ],
        "crewai": [
            "crewai>=0.1.0",
        ],
    },
    keywords="markdown, llm, template, ai, kimfe",
)