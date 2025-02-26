from setuptools import setup, find_packages

setup(
    name="bloomy-mcp",
    version="0.1.0",
    description="MCP server for Bloom Growth GraphQL API",
    author="Bloom Growth",
    author_email="support@bloomgrowth.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "mcp>=1.2.0",
        "gql[all]>=3.4.1",
        "python-dotenv>=1.0.0",
        "httpx>=0.25.0",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "bloomy-mcp=bloomy_mcp.server:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
