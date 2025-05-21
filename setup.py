from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="document-qa-agent",
    version="1.0.0",
    author="Mohamed Eltaher",
    author_email="dev.eltaher@gmail.com",
    description="A document QA agent built with LangChain and Ollama",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/document-qa-agent",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",    install_requires=[
        "langchain>=0.1.0",
        "langchain-community>=0.0.10",
        "langchain-core>=0.1.10",
        "langchain-chroma>=0.0.1",
        "langchain-huggingface>=0.0.1",
        "langchain-ollama>=0.0.1",
        "fastapi>=0.100.0",
        "uvicorn>=0.23.0",
        "python-multipart>=0.0.6",
        "chromadb>=0.4.18",
        "pydantic>=2.0.0",
        "pypdf>=3.15.1",
        "sentence-transformers>=2.2.2"
    ],
)
