#pragma once

#include <mpi_proto.h>
#include <petscconf.h>
#include <petscerror.h>
#include <petscmacros.h>
#include <petscoptions.h>
#include <petscsys.h>
#include <petscsystypes.h>

#define PETSC_FAIL ((PetscErrorCode)1)
#define user_petsc_check(flag, message) \
    PetscCheck(flag, PETSC_COMM_WORLD, PETSC_ERR_USER, message)

PetscErrorCode user_is_ok(int x, int y) {
    return (PetscErrorCode)(x!=y);
}

PetscErrorCode user_init_mpi_uniprocessor() {
    PetscMPIInt size;
    PetscCallMPI(MPI_Comm_size(PETSC_COMM_WORLD, &size));
    user_petsc_check(size == 1, "[PETSC_ERR_WRONG_MPI_SIZE] 非并行程序");
    return PETSC_SUCCESS;
}

PetscErrorCode user_options_get_boolean(const char name[], PetscBool *ivalue, PetscBool *set) {
    return PetscOptionsGetBool(PETSC_NULLPTR, PETSC_NULLPTR, name, ivalue, set);
}

PetscErrorCode user_options_get_boolean_default(const char name[], PetscBool *ivalue) {
    return PetscOptionsGetBool(PETSC_NULLPTR, PETSC_NULLPTR, name, ivalue, PETSC_NULLPTR);
}

PetscErrorCode user_options_get_integer(const char name[], PetscInt *ivalue, PetscBool *set) {
    return PetscOptionsGetInt(PETSC_NULLPTR, PETSC_NULLPTR, name, ivalue, set);
}

PetscErrorCode user_options_get_real(const char name[], PetscReal *dvalue, PetscBool *set) {
    return PetscOptionsGetReal(PETSC_NULLPTR, PETSC_NULLPTR, name, dvalue, set);
}

PetscErrorCode user_options_get_string(const char name[], char string[], size_t len, PetscBool *set) {
    return PetscOptionsGetString(PETSC_NULLPTR, PETSC_NULLPTR, name, string, len, set);
}

PetscErrorCode user_options_get_integer_default(const char name[], PetscInt *ivalue, PetscInt default_) {
    PetscBool set;
    PetscErrorCode ierr = user_options_get_integer(name, ivalue, &set);
    if (!set) {
        *ivalue = default_;
    }
    return ierr;
}

PetscErrorCode user_options_get_real_default(const char name[], PetscReal *dvalue, PetscReal default_) {
    PetscBool set;
    PetscErrorCode ierr = user_options_get_real(name, dvalue, &set);
    if (!set) {
        *dvalue = default_;
    }
    return ierr;
}

PetscErrorCode user_options_get_path(const char name[], char string[], PetscBool *set) {
    return user_options_get_string(name, string, PETSC_MAX_PATH_LEN, set);
}
