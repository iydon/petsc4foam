#include <mpi.h>
#include <petscerror.h>
#include <petscksp.h>
#include <petscmat.h>
#include <petscsys.h>
#include <petscsystypes.h>
#include <petsctime.h>
#include <petscvec.h>
#include <petscviewer.h>
#include <petscviewertypes.h>

#include "util.h"

static const PetscChar help[] =
    "Test for KSPSolve (Ax=b)\n"
    "\n"
    "Options:\n"
    "  --A       TEXT     A matrix path\n"
    "  --number  INTEGER  Perform exactly number runs\n";

typedef struct {
    PetscChar a[PETSC_MAX_PATH_LEN];
    PetscInt number;
    // flags
    PetscBool flag_a;
} AppCtx;

PetscErrorCode user_init_options(AppCtx *);
PetscErrorCode user_solve(AppCtx *);

int main(int argc, char **args) {
    AppCtx user;
    PetscCall(
           PetscInitialize(&argc, &args, (char *)0, help)
        || user_init_options(&user)
        || user_solve(&user)
        || PetscFinalize()
    );
    return 0;
}

PetscErrorCode user_init_options(AppCtx *ctx) {
    PetscCall(
           user_options_get_path("--A", ctx->a, &ctx->flag_a)
        || user_options_get_integer_default("--number", &ctx->number, 1000)
    );
    // a
    if (!ctx->flag_a) {
        PetscPrintf(PETSC_COMM_WORLD, help);
        exit(0);
    }
    return PETSC_SUCCESS;
}

PetscErrorCode user_solve(AppCtx *ctx) {
    KSP ksp;
    Mat a;
    PC pc;
    PetscInt its, size;
    PetscLogDouble mems = 0.0, times = 0.0, mem, tic, toc;
    PetscReal rnorm;
    PetscViewer viewer;
    Vec b, x, x0;
    PetscErrorCode ierr = PETSC_SUCCESS;
    // load
    ierr = ierr
        || PetscViewerBinaryOpen(PETSC_COMM_WORLD, ctx->a, FILE_MODE_READ, &viewer)
        || MatCreate(PETSC_COMM_WORLD, &a)
        || MatLoad(a, viewer)
        || PetscViewerDestroy(&viewer)
        || MatGetSize(a, &size, PETSC_NULLPTR)
        || VecCreate(PETSC_COMM_WORLD, &x)
        || VecSetFromOptions(x)
        || VecSetSizes(x, size, PETSC_DETERMINE)
        || VecSet(x, 1.0)
        || VecDuplicate(x, &b)
        || MatMult(a, x, b);
    // solve
    for (PetscInt ith = 0; ith < ctx->number; ith++) {
        ierr = ierr
            || VecDuplicate(x, &x0)
            || KSPCreate(PETSC_COMM_WORLD, &ksp)
            || KSPSetFromOptions(ksp)
            || KSPGetPC(ksp, &pc)
            || PCSetFromOptions(pc)
            || KSPSetOperators(ksp, a, a)
            || PetscTime(&toc)
            || KSPSolve(ksp, b, x0)
            || PetscTime(&tic)
            || PetscMemoryGetCurrentUsage(&mem);
        if (0 == ierr) {
            if (0 == ith) {
                ierr = ierr
                    || KSPGetIterationNumber(ksp, &its)
                    || KSPGetResidualNorm(ksp, &rnorm);
            }
            mems += mem;
            times += tic - toc;
        }
        ierr = ierr || KSPDestroy(&ksp);
    }
    // post
    ierr = ierr
        || PetscPrintf(PETSC_COMM_WORLD, "iter\t%d\n", its)
        || PetscPrintf(PETSC_COMM_WORLD, "mem\t%le\n", mems/ctx->number)
        || PetscPrintf(PETSC_COMM_WORLD, "norm\t%le\n", rnorm)
        || PetscPrintf(PETSC_COMM_WORLD, "time\t%le\n", times/ctx->number);
    return ierr
        || VecDestroy(&x0)
        || VecDestroy(&x)
        || VecDestroy(&b)
        || MatDestroy(&a);
}
