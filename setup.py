import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='tweego',
    version='0.1.0',
    author="Aveek Saha",
    author_email="aveek.s98@gmail.com",
    url='https://github.com/Aveek-Saha/tweego',
    description="Generate ego networks for users from Twitter.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages= setuptools.find_packages(),
    include_package_data=True,
    py_modules=['tweego'],
    install_requires=[
        'Click',
        'networkx',
        'TwitterAPI',
        'tqdm'
    ],
    entry_points={
        'console_scripts': [
            'tweego = tweego:cli',
        ],
    },
)