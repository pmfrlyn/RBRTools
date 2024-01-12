from setuptools import setup, find_packages

setup(
    name='rbr_tools',
    version='0.1.0',
    packages=find_packages(),
    py_modules=['rbr_run_plotter', 'rbr_influx_telemetry_sender', 'rbr_setup_compare'],
    install_requires=[
        'pyparsing',
        'influxdb-client',
        'matplotlib',
        'click'
    ],
    entry_points={
        'console_scripts': [
            'rbr_run_plotter = rbr_run_plotter:cli',
            'rbr_influx_telemetry_sender = rbr_influx_telemetry_sender:cli',
            'rbr_setup_compare = rbr_setup_compare:main'
        ],
    },
)