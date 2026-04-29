from setuptools import setup, find_packages

setup(
    name="nychforge",
    version="0.1.0",
    description="Bounded Gated Recursive Self-Editing AI Builder",
    author="N",
    packages=find_packages(),
    install_requires=[
        "google-genai>=1.0",
        "rich>=13.0",
        "typer>=0.9",
        "pydantic>=2.0",
        "gradio>=4.0",
    ],
    entry_points={
        "console_scripts": [
            "nychforge=cli.run:main",
        ],
    },
    python_requires=">=3.10",
)
