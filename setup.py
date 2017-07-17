from setuptools import setup, find_packages


def read(*filenames, **kwargs):
    import io
    from os.path import join, dirname
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(join(dirname(__file__), filename), encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)


setup(
    name='os-rotatefile',
    version=read('src/os_rotatefile/VERSION'),
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    license='MIT License',
    description='Reading and writing size rotate file.',
    long_description=open('README.md').read(),
    author='Ozzy',
    author_email='cfhamlet@gmail.com',
    url='https://github.com/cfhamlet/os-ratatefile',
    zip_safe=False,
    install_requires=['six>=1.5.2',],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
    ])