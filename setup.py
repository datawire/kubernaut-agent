import versioneer

from setuptools import setup, find_packages

setup(
    name="kubernaut-agent",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    install_requires=[
        "autobahn",
        "click"
    ],
    entry_points="""
        [console_scripts]
        kubernaut-agent=kubernaut.agent:agent
    """,
    author="datawire.io",
    author_email="dev@datawire.io",
    url="https://github.com/datawire/kubernaut-agent",
    download_url="https://github.com/datawire/kubernaut-agent/tarball/{}".format(versioneer.get_version()),
    keywords=[
        "testing",
        "development",
        "kubernetes",
        "microservices"
    ],
    classifiers=[],
)
