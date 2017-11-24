from setuptools import setup, find_packages


setup(
    name='dumpwik',
    version='0.8',
    packages=find_packages('src'),
    package_dir={
        '': 'src',
    },
    include_package_data=True,
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
