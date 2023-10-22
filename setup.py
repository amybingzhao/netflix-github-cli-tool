from setuptools import setup, find_packages

setup(
    name='github_organization_repo_explorer',
    description='CLI tool for finding the top N repos by requested criteria for a given Github org.',
    version='1.0.0',
    author='amybzhao',
    install_requires=[
        'pygithub==2.1.1',
        'python-dotenv==1.0.0',
    ]
)