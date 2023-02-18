from pathlib import Path

import setuptools

with open('requires.txt', encoding='utf-8') as f:
    requires = f.read().strip().splitlines()
with open('CHANGELOG.md', encoding='utf-8') as f:
    changelog = f.read()
with open('README.md', encoding='utf-8') as f:
    readme = f.read()
readme += f'\n\n# CHANGELOG\n\n{changelog}'

extras_require = {}
for require in Path('extra_requires').glob('*_*.txt'):
    with open(require, encoding='UTF-8') as f:
        extras_require[require.name.split('.', 1)[0].rsplit('_', 1)[-1].casefold()] = f.read().strip().splitlines()
extras_require['all'] = sum(extras_require.values(), requires)

setuptools.setup(
    name="FastDub",
    version="3.5.1",

    description="A Python CLI package "
                "for voice over subtitles, with the ability to embed in video, audio ducking, "
                "and dynamic voice changer for a single track; "
                "auto translating; "
                "download and upload to YouTube supports",

    long_description=readme,
    long_description_content_type="text/markdown",

    author="Nikita (NIKDISSV)",
    author_email='nikdissv@proton.me',

    packages=setuptools.find_packages(),

    install_requires=requires,
    extras_require=extras_require,

    project_urls={
        'Download Voices': 'https://rhvoice.su/voices',
        'GitHub': 'https://github.com/NIKDISSV-Forever/FastDub',
        'YouTube': 'https://www.youtube.com/channel/UC8JV3zPSVm9EKSWD1XdkQvw',
    },

    license='MIT',
    python_requires='>=3.8',

    classifiers=[
        'Development Status :: 5 - Production/Stable',

        'Environment :: Console',

        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Other Audience',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Telecommunications Industry',

        'License :: OSI Approved',
        'License :: OSI Approved :: MIT License',

        'Operating System :: OS Independent',

        'Natural Language :: English',
        'Natural Language :: Russian',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',

        'Topic :: Multimedia',
        'Topic :: Multimedia :: Sound/Audio',
        'Topic :: Multimedia :: Sound/Audio :: Analysis',
        'Topic :: Multimedia :: Sound/Audio :: Conversion',
        'Topic :: Multimedia :: Sound/Audio :: Speech',
        'Topic :: Multimedia :: Video',
        'Topic :: Multimedia :: Video :: Conversion',
        'Topic :: Software Development :: Internationalization',
        'Topic :: Utilities',

        'Typing :: Typed',
    ],

    keywords=['dubbing', 'voicing',
              'fastdub', 'JustDub', 'SpeedDub',
              'offline', 'free', 'easiest',
              'subtitles', 'videos', 'veed', 'fast'],
)
