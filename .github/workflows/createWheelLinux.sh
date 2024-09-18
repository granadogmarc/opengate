#!/bin/bash

set -e -x
echo ${PYTHONFOLDER}
cd /home/core/
export PATH=/software/cmake/cmake-3.18.2-Linux-x86_64/bin/:${PATH}
source /software/geant4/bin/geant4make.sh
export CMAKE_PREFIX_PATH=/software/geant4/bin:/software/itk/bin/:${CMAKE_PREFIX_PATH}
mkdir opengate_core/plugins
cp -r /opt/Qt/6.7.2/gcc_64/plugins/platforms opengate_core/plugins/
cp -r /opt/Qt/6.7.2/gcc_64/plugins/imageformats opengate_core/plugins/
cp -r /opt/Qt/6.7.2/gcc_64/plugins/xcbglintegrations opengate_core/plugins/
/opt/python/${PYTHONFOLDER}/bin/pip install wget colored
/opt/python/${PYTHONFOLDER}/bin/python setup.py sdist bdist_wheel
auditwheel repair /home/core/dist/*.whl -w /software/wheelhouse/ --plat "manylinux_2_28_x86_64"
cp -r /software/wheelhouse /home/
#/opt/python/${PYTHONFOLDER}/bin/pip install twine
#/opt/python/${PYTHONFOLDER}/bin/twine upload --repository-url https://test.pypi.org/legacy/ wheelhouse/*manylinux2014*.whl
