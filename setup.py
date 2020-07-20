from setuptools import setup, find_packages

setup(
    name='DiscordantDeamonPy',
    version='1.0',
    description='Game Server Management Bot for Discord',
    author='Deamon',
    author_email='dev@deamon.info',
    # scripts=[],
    # entry_points={
    #     "console_scripts": [
    #         "bot = bot2:main_func"
    #     ]
    # },
    packages=find_packages(),
    install_requires=['discord.py'],
    # package_data={
    #     "": ["*.py", "*.json"]
    # },
    url="https://github.com/dittopower/DiscordantDeamonPy",
    keywords="discord server host management game_server"
)
