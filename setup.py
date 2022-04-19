import setuptools

with open('requires.txt', encoding='utf-8') as f:
    requires = f.read().splitlines()
setuptools.setup(
    name="PyFastDub",
    description="A Python package (+CLI) for voice over subtitles, with the ability to embed in video, audio ducking, "
                "and dynamic voice changer for a single track.",
    version="2.0.0",
    author="Nikita (NIKDISSV)",
    install_requires=requires,
    author_email='nikdissv.forever@protonmail.com',
    project_urls={
        'Download Voices': 'https://rhvoice.su/voices/',
    },
    packages=setuptools.find_packages(),
    python_requires='>=3.8',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Typing :: Typed',
    ]
)
