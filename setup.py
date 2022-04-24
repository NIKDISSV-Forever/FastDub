import setuptools

with open('requires.txt', encoding='UTF-8') as f:
    requires = f.read().splitlines()
with open('yt_requires.txt', encoding='UTF-8') as f:
    yt_requires = f.read().splitlines()
with open('tr_requires.txt', encoding='UTF-8') as f:
    tr_requires = f.read().splitlines()

with open('README.md', encoding='UTF-8') as f:
    readme = f.read()

setuptools.setup(
    name="PyFastDub",
    description="A Python package (+CLI) for voice over subtitles, with the ability to embed in video, audio ducking, "
                "and dynamic voice changer for a single track.",
    long_description=readme,
    long_description_content_type="text/markdown",
    version="2.4.1",
    author="Nikita (NIKDISSV)",
    install_requires=requires,
    extras_require={'YT': yt_requires, 'TR': tr_requires},
    author_email='nikdissv.forever@protonmail.com',
    project_urls={
        'Download Voices': 'https://rhvoice.su/voices/',
        'GitHub': 'https://github.com/NIKDISSV-Forever/FastDub'
    },
    packages=setuptools.find_packages(),
    python_requires='>=3.8<3.11',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Typing :: Typed',
        'Development Status :: 4 - Beta',
    ]
)
