#pip install protobuf
// for python 34
conda  install -c dhirschfeld protobuf


Help pour compiler sous win avec py35
https://www.mail-archive.com/search?l=protobuf@googlegroups.com&q=subject:%22%5C%5Bprotobuf%5C%5D+unresolved+external+symbol+with+python+build%22&o=newest&f=1
https://github.com/google/protobuf/commit/1858ac9b42c167ab6d89b929c075872d740eb0b5

install protobuf and compile it
from the mscv2015 command prompt shell
https://github.com/google/protobuf/blob/master/cmake/README.md

make the cmake
cmake -G "NMake Makefiles" ^
 -DCMAKE_BUILD_TYPE=Release ^
 -DCMAKE_INSTALL_PREFIX=../../../../install ^
 ../..

call the nmake with the right param
nmake USER_C_FLAGS="/DPROTOBUF_USE_DLLS"

in anaconda
in distutils.cfg
	compiler=msvc

and install the build tools vc2015
redist
http://landinghub.visualstudio.com/visual-cpp-build-tools


in python/setup.py comment part of code
extra_compile_args = []#'-Wno-write-strings',
                          # '-Wno-invalid-offsetof',
                          # '-Wno-sign-compare']
copy the compile release protoc in the src folder
set PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=cpp
python setup.py build --cpp_implementation
python setup.py test --cpp_implementation
python setup.py install --cpp_implementation


before launching the python
set PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=cpp

