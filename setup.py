import setuptools

with open("readme.md", "r") as f:
    readme = f.read()

setuptools.setup(
    name="sportschau_bl_data",
    version="0.1",
    author="znstrider",
    author_email="mindfulstrider@gmail.com",
    description="Sportschau.de Bundesliga Data",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/znstrider/sportschau_bl_data",
    packages=setuptools.find_packages(),
    package_data={
        # If any package contains *.txt or *.rst files, include them:
        "": ["*.txt"]
    },
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3.7",
    ],
    python_requires=">=3.7",
)
