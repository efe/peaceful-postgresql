from setuptools import setup, find_packages

setup(
    name="peaceful-postgresql",
    version="0.1.0",
    author="Efe Öge",
    author_email="efeoge@example.com",
    description="A tool for detecting potential downtime during PostgreSQL schema modifications.",
    url="https://github.com/efe/peaceful-postgresql",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Database",
        "Topic :: Database :: Database Engines/Servers",
        "Topic :: Database :: Front-Ends",
        "Framework :: Django",
        "Framework :: SQLAlchemy",
        "Framework :: Alembic",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        "sqlparse>=0.4.0",
    ],
) 