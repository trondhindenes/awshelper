from setuptools import setup

setup(
    name='aws_helper',
    version='0.1',
    description='helps you run aws stuff',
    url='http://github.com/storborg/funniest',
    author='Trond Hindenes',
    author_email='trond@hindenes.com',
    license='MIT',
    packages=['awshelper'],
    zip_safe=False,
    entry_points={
        'console_scripts': ['awshelper=aws_helper.cmd_line:main'],
    }
)
