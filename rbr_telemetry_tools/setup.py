from setuptools import setup, find_packages

setup(
    name='rbr_telemetry_tools',
    version='0.1.0',
    packages=find_packages(),
    py_modules=['rbr_run_plotter', 'rbr_influx_telemetry_sender'],
    install_requires=[
        'pyparsing',
        'influxdb-client',
        'matplotlib',
        'click'
    ],
    entry_points={
        'console_scripts': [
            'rbr_run_plotter = rbr_run_plotter:cli',
        ],
    },
)