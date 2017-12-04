from setuptools import setup, find_packages


setup(
    name='dumpwik',
    use_scm_version={
        'write_to': 'src/dumpwik/_version.py',
    },
    packages=find_packages('src'),
    package_dir={
        '': 'src',
    },
    include_package_data=True,
    setup_requires=[
        'setuptools_scm',
    ],
    install_requires=[
        'Click',
        'mysql-connector-python',
    ],
    entry_points={
        'console_scripts': [
            'dumpwik=dumpwik.entrypoint:main',
        ],
    },
)
