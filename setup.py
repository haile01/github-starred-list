from setuptools import setup, find_packages

setup(
    name="gh-list",
    version="0.0.1",
    entry_points={
        'console_scripts': [
            'gh-list=gh_list.cli:main',
        ],
    },
    exclude_package_data={'': ['test.py']},
    packages=find_packages(),
    include_package_data=True,
)