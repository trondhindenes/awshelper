from setuptools import setup

setup(
    name='awshelper',
    version='0.4',
    description='helps you run aws commands with sso-based credentials',
    url='https://github.com/trondhindenes/awshelper',
    author='Trond Hindenes',
    author_email='trond@hindenes.com',
    license='MIT',
    packages=['aws_helper'],
    zip_safe=False,
    entry_points={
        'console_scripts': ['awshelper=aws_helper.cmd_line:main'],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
