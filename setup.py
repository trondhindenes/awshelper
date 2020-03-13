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
    },
    classifiers=[
        'Development Status :: 3 - Alpha',  # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',  # Define that your audience are developers
        'License :: OSI Approved :: MIT License',  # Again, pick a license
        'Programming Language :: Python :: 3',  # Specify which pyhton versions that you want to support
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
