from setuptools import setup, find_packages

install_requires = ['xmpppy', 'jabberbot', 'django']

classifiers = """
Intended Audience :: Developers
Intended Audience :: Information Technology
Framework :: Django
License :: OSI Approved :: GNU General Public License (GPL)
Programming Language :: Python
Development Status :: 3 - Alpha
Topic :: Communications :: Chat
"""

setup( 
    name = 'djabberdjaw',
    version = '0.1',  # remember to update djabberdjaw/__init__.py on release!
    url = 'http://matienzo.org/project/djabberdjaw',
    author = 'Mark A. Matienzo',
    author_email = 'mark@matienzo.org',
    license = 'GPL',
    packages = find_packages(),
    install_requires = install_requires,
    description = 'A Jabber bot with a Django-backend for user management ',
    classifiers = filter(None, classifiers.split('\n')),
)
