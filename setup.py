from setuptools import setup, find_packages

version = '0.1.5'

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='ms-launcher',
    version=version,
    license='BSD-3-Clause license',
    author='Ivan Ms',
    author_email='ivanms.ept@gmail.com',
    description='BombSquad plugin that filters the list of game servers and simplifies access to them',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Ms-company-BombSquad/ms-launcher',
    download_url=f'https://github.com/Ms-company-BombSquad/ms-launcher/archive/v{version}.zip',
    packages=['ms_launcher'],
)
