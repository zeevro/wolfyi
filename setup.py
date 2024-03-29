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
        'appdirs',
        'flask',
        'sqlalchemy',
        'flask_admin',
        'flask_login',
        'flask_sqlalchemy',
    ],
    entry_points=dict(
        console_scripts=[
            'wolfyi-server = wolfyi.run:main',
            'wolfyi-add-user = wolfyi.add_user:main',
            'wolfyi-create-invite = wolfyi.create_invite:main',
        ],
    ),
)
