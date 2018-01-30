"""
Starcraft BW docker launcher.
"""

# Always prefer setuptools over distutils
from setuptools import setup

from scbw_mq import VERSION

setup(
    name='scbw_mq',
    version=VERSION,
    description='Message queues for distributed use of scbw package',
    long_description="Message queue for starcraft workers."
                     "Allow spawning of multiple workers that play starcraft games, orchestrated by RabbitMQ."
                     "See https://github.com/Games-and-Simulations/sc-mq for more information.",
    url='https://github.com/Games-and-Simulations/sc-mq',
    author='Michal Sustr',
    author_email='michal.sustr@aic.fel.cvut.cz',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.6',
    ],
    keywords='starcraft broodwar rabbitmq tournament',
    install_requires=['pika',
                      'coloredlogs',
                      'tqdm',
                      'scbw'],
    extras_require={
    },
    packages=['scbw_mq',
              'scbw_mq.parser',
              'scbw_mq.tournament'],
    entry_points={  # Optional
        'console_scripts': [
            'scbw.tournament.consume=scbw_mq.tournament.cli:consumer',
            'scbw.tournament.produce=scbw_mq.tournament.cli:producer',
            'scbw.parser.produce=scbw_mq.parser.cli:producer',
            'scbw.parser.consume=scbw_mq.parser.cli:consumer',

        ],
    },
    python_requires='>=3.6',
)
