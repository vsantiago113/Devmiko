from setuptools import setup

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='Devmiko',
    packages=['Devmiko'],
    version='0.0.3',
    license='MIT',
    description='A SSH client for systems network automation that uses paramiko.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Victor M Santiago',
    author_email='vsantiago113sec@gmail.com',
    url='https://github.com/vsantiago113/Devmiko',
    download_url='https://github.com/vsantiago113/Devmiko/archive/0.0.3.tar.gz',
    keywords=['paramiko', 'firepower', 'cisco', 'ftd', 'ssh'],
    python_requires='>=3.4.0',
    install_requires=[
        'paramiko', 'tqdm'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
