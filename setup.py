from setuptools import setup, find_packages

with open('README.rst') as f:
    long_description = ''.join(f.readlines())

setup(
    name='filabel_cvut',
    version='0.3',
    keywords='github labels management pull-requests globs',
    description='Simple CLI & WEB tool for labeling GitHub PRs using globs',
    long_description=long_description,
    author='Marek Suchánek',
    author_email='suchama4@fit.cvut.cz',
    license='MIT',
    url='https://github.com/cvut/filabel',
    zip_safe=False,
    packages=find_packages(),
    package_data={
        'filabel': [
            'static/*.css',
            'templates/*.html',
        ]
    },
    entry_points={
        'console_scripts': [
            'filabel = filabel:cli',
        ]
    },
    install_requires=[
        'click',
        'Flask',
        'jinja2',
        'requests',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development',
        'Topic :: Utilities',
    ],
)
