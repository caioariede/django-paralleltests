from setuptools import setup, find_packages


VERSION = '0.1a'


setup(
    name='django-paralleltests',
    version=VERSION,
    description="Django Test Runner to run tests in parallel",
    author="Caio Ariede",
    author_email="caio.ariede@gmail.com",
    url="http://github.com/caioariede/django-paralleltests",
    license="MIT",
    zip_safe=False,
    platforms=["any"],
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
    ],
    include_package_data=True,
    install_requires=[
        'six',
    ],
)
