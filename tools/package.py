#!/usr/bin/env python

# This is a horrible script, but cpack is rather bad
# and won't let us merge Debug+Release on windows.

import os
import sys
import subprocess
import shutil

shutil.rmtree('build_pkg')

version = None
with open('VERSION', 'r') as f:
  version = f.read().strip()

ARCH = sys.argv[1]
ROOT = 'build_pkg/root'
ROOT_PACKAGE = 'libresin-%s-%s' % (version, ARCH)
ROOT_PACKAGE_SRC = 'libresin-%s-src' % (version)
ROOT_FULL = ROOT + '/' + ROOT_PACKAGE
ROOT_FULL_SRC = ROOT + '/' + ROOT_PACKAGE_SRC
TREE = 'build_pkg/tree'
DIST = 'dist'

os.makedirs(ROOT, exist_ok=True)
os.makedirs(TREE, exist_ok=True)
os.makedirs(DIST, exist_ok=True)

if os.name == 'nt':
  if ARCH == 'win32':
    subprocess.run(['cmake', '-S', '.', '-B', TREE, '-DCMAKE_INSTALL_PREFIX=%s' % ROOT_FULL, '-A', 'Win32'])
  else:
    subprocess.run(['cmake', '-S', '.', '-B', TREE, '-DCMAKE_INSTALL_PREFIX=%s' % ROOT_FULL])
  subprocess.run(['cmake', '--build', TREE, '--config', 'Debug', '--target', 'install'])
  subprocess.run(['cmake', '--build', TREE, '--config', 'Release', '--target', 'install'])
else:
  subprocess.run(['cmake', '-S', '.', '-B', TREE, '-DCMAKE_INSTALL_PREFIX=%s' % ROOT_FULL, '-DCMAKE_BUILD_TYPE=Release'])
  subprocess.run(['cmake', '--build', TREE, '--target', 'install'])

package     = '%s/libresin-%s-%s' % (DIST, version, ARCH)
package_src = '%s/libresin-%s-src' % (DIST, version)

shutil.make_archive(package, 'xztar', ROOT)
shutil.rmtree(ROOT_FULL)

# Source
os.makedirs(ROOT_FULL_SRC, exist_ok=True)
shutil.copy('CMakeLists.txt', ROOT_FULL_SRC + '/CMakeLists.txt')
shutil.copy('LICENSE', ROOT_FULL_SRC + '/LICENSE')
shutil.copy('README.md', ROOT_FULL_SRC + '/README.md')
shutil.copy('VERSION', ROOT_FULL_SRC + '/VERSION')
shutil.copytree('cmake', ROOT_FULL_SRC + '/cmake', dirs_exist_ok=True)
shutil.copytree('src', ROOT_FULL_SRC + '/src', dirs_exist_ok=True)
shutil.copytree('include', ROOT_FULL_SRC + '/include', dirs_exist_ok=True)
shutil.copytree(TREE + '/gen/src', ROOT_FULL_SRC + '/src', dirs_exist_ok=True)
shutil.copytree(TREE + '/gen/include', ROOT_FULL_SRC + '/include', dirs_exist_ok=True)

shutil.make_archive(package_src, 'xztar', ROOT)
