from distutils.core import setup

# Idea borrowed from http://cburgmer.posterous.com/pip-requirementstxt-and-setuppy
install_requires, dependency_links = [], []
for line in open('requirements.txt'):
    line = line.strip()
    if line.startswith('-e'):
        dependency_links.append(line[2:].strip())
    elif line:
        install_requires.append(line)

setup(
    name='django-webauth',
    description="WebAuth/LDAP integration for Django",
    author='Oxford University Computing Services',
    author_email='infodev@oucs.ox.ac.uk',
    version='0.1',
    license='BSD',
    url='https://github.com/oucs/django-webauth',
    long_description=open('README.rst').read(),
    classifiers=['Development Status :: 4 - Beta',
                 'Framework :: Django',
                 'License :: OSI Approved :: BSD License',
                 'Natural Language :: English',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python',
                 'Topic :: Internet :: WWW/HTTP :: Dynamic Content'],
    packages=['django_webauth'],
    data_files=[['django_webauth/templates/webauth', ['django_webauth/templates/webauth/base.html',
                                                      'django_webauth/templates/webauth/logged_out.html']]],
    install_requires=install_requires,
    dependency_links=dependency_links,
)
