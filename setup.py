from setuptools import find_packages, setup


setup(
    name='wolfyi',
    version='0.0.1',
    url='https://github.com/zeevro/wolfyi',
    download_url='https://github.com/zeevro/wolfyi/archive/master.zip',
    author='Zeev Rotshtein',
    author_email='zeevro@gmail.com',
    maintainer='Zeev Rotshtein',
    maintainer_email='zeevro@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Framework :: Flask',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    ],
    license=None,
    description='A simple URL shortener',
    keywords=[
        'URL shortener'
    ],
    zip_safe=False,
    package_dir={
        '': 'src',
    },
    packages=find_packages('src'),
    include_package_data=True,
    install_requires=[
        'flask',
        'sqlalchemy',
        'flask_login',
        'flask_sqlalchemy',
    ],
    entry_points=dict(
        console_scripts=[
            'wolfyi = wolfyi.run:main',
        ],
    ),
)
