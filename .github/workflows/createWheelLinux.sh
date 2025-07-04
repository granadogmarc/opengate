#!/bin/bash

set -e -x
echo ${PYTHONFOLDER}
cd /home/core/
export PATH=/software/cmake/cmake/bin/:${PATH}
source /software/geant4/bin/geant4make.sh
export CMAKE_PREFIX_PATH=/software/geant4/bin:/software/itk/bin/:${CMAKE_PREFIX_PATH}
. /opt/rh/gcc-toolset-14/enable
mkdir opengate_core/plugins
cp -r /lib64/qt6/plugins/platforms/* opengate_core/plugins/
cp -r /lib64/qt6/plugins/imageformats opengate_core/plugins/
/opt/python/${PYTHONFOLDER}/bin/pip install wget colored setuptools
/opt/python/${PYTHONFOLDER}/bin/python setup.py sdist bdist_wheel
archi=`uname -m`
if [ "$(uname -m)" = "aarch64" ]; then
  auditwheel repair /home/core/dist/*.whl -w /software/wheelhouse/ --plat "manylinux_2_34_aarch64"
else
  auditwheel repair /home/core/dist/*.whl -w /software/wheelhouse/ --plat "manylinux_2_34_x86_64"
fi
cp -r /software/wheelhouse /home/
#/opt/python/${PYTHONFOLDER}/bin/pip install twine
#/opt/python/${PYTHONFOLDER}/bin/twine upload --repository-url https://test.pypi.org/legacy/ wheelhouse/*manylinux2014*.whl
