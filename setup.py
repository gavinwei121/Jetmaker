from setuptools import setup, find_packages

setup(
    name='jetmaker',  # Replace with your unique package name
    version='0.13',
    packages=find_packages(),
    install_requires=[
        # List any dependencies here
        'cloudpickle',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    description='A brief description of your module',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
)




