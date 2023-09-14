cmake_minimum_required(VERSION 3.12)

project(bin)

set(CMAKE_C_COMPILER mpicc)
set(CMAKE_CXX_COMPILER mpicxx)
add_definitions($ENV{PCC_FLAGS})
include_directories(${PETSC_PREFIX}/include)
link_directories(${PETSC_PREFIX}/lib)

set(PROGRAM_TEST4SOLVE test4solve)
add_executable(${PROGRAM_TEST4SOLVE} test4solve.c util.h)
target_link_libraries(${PROGRAM_TEST4SOLVE} $ENV{PETSC_LIB})
install(TARGETS ${PROGRAM_TEST4SOLVE} RUNTIME DESTINATION $ENV{PETSC_USER_BIN})

set(PROGRAM_TXT2BIN txt2bin)
add_executable(${PROGRAM_TXT2BIN} txt2bin.c util.h)
target_link_libraries(${PROGRAM_TXT2BIN} $ENV{PETSC_LIB})
install(TARGETS ${PROGRAM_TXT2BIN} RUNTIME DESTINATION $ENV{PETSC_USER_BIN})
