#include <mpi.h>
#include <petscerror.h>
#include <petscmat.h>
#include <petscsys.h>
#include <petscsystypes.h>
#include <petscvec.h>
#include <petscviewer.h>
#include <petscviewertypes.h>

#include "util.h"

#define BUFFER_LENGTH 99
#define TYPE_LENGTH 3

static const PetscChar help[] =
    "Convert text format to PETSc binary\n"
    "\n"
    "Options:\n"
    "  --type     TEXT     mtx or rhs\n"
    "  --in       TEXT     input path\n"
    "  --out      TEXT     output path\n"
    "  --base     INTEGER  0-base, 1-base matrix, etc.\n"
    "  --complex           complex matrix or vector\n"
    "  --real              real matrix or vector\n"
    "  --stdout            viewer stdout\n";
static const PetscChar types[][TYPE_LENGTH+1] = {"mtx", "rhs"};

typedef struct {
    PetscBool is_complex, is_real, is_stdout;
    PetscInt base;
    PetscChar type[TYPE_LENGTH+1], in[PETSC_MAX_PATH_LEN], out[PETSC_MAX_PATH_LEN];
    // flags
    PetscBool flag_real, flag_type, flag_in, flag_out;
} AppCtx;

PetscErrorCode user_init_options(AppCtx *);
PetscErrorCode user_saves(AppCtx *);
PetscErrorCode user_save_vector(AppCtx *);
PetscErrorCode user_save_matrix(AppCtx *);

int main(int argc, char **args) {
    AppCtx user;
    PetscCall(
           PetscInitialize(&argc, &args, (char *)0, help)
        || user_init_mpi_uniprocessor()
        || user_init_options(&user)
        || user_saves(&user)
        || PetscFinalize()
    );
    return 0;
}

PetscErrorCode user_init_options(AppCtx *ctx) {
    PetscBool flag;
    PetscChar *pch;
    PetscInt ith;
    PetscCall(
           user_options_get_boolean("--real", &ctx->is_real, &ctx->flag_real)
        || user_options_get_boolean_default("--complex", &ctx->is_complex)
        || user_options_get_boolean_default("--stdout", &ctx->is_stdout)
        || user_options_get_integer_default("--base", &ctx->base, 0)
        || user_options_get_path("--in", ctx->in, &ctx->flag_in)
        || user_options_get_path("--out", ctx->out, &ctx->flag_out)
        || user_options_get_string("--type", ctx->type, sizeof(ctx->type), &ctx->flag_type)
    );
    // is_complex
    if (ctx->flag_real) {
        ctx->is_complex = !ctx->is_real;
    }
    // is_stdout
    if (!ctx->flag_out) {
        ctx->is_stdout = PETSC_TRUE;
    }
    // in
    if (!ctx->flag_in) {
        PetscPrintf(PETSC_COMM_WORLD, help);
        exit(0);
    }
    // type
    if (!ctx->flag_type) {
        pch = strrchr(ctx->in, '.');
        flag = pch != NULL && ctx->in - pch + strlen(ctx->in) - 1 <= TYPE_LENGTH;
        user_petsc_check(flag, "[PETSC_ERR_ARG_WRONGSTATE] 参数 type 未指定，或者没有根据参数 in 推断出来");
        strncpy(ctx->type, pch+1, TYPE_LENGTH);
    }
    flag = PETSC_FALSE;
    for (ith = 0; ith < sizeof(types) / (TYPE_LENGTH + 1); ith++) {
        if (0 == strcmp(ctx->type, types[ith])) {
            flag = PETSC_TRUE;
        }
    }
    user_petsc_check(flag, "[PETSC_ERR_ARG_UNKNOWN_TYPE] 参数 type 必须为 mtx 或者 rhs");
    return PETSC_SUCCESS;
}

PetscErrorCode user_saves(AppCtx *ctx) {
    if (0 == strcmp(ctx->type, "rhs")) {
        return user_save_vector(ctx);
    }
    if (0 == strcmp(ctx->type, "mtx")) {
        return user_save_matrix(ctx);
    }
    return PETSC_FAIL;
}

PetscErrorCode user_save_vector(AppCtx *ctx) {
    FILE *file;
    PetscInt ith, number;
    PetscInt *indices;
    PetscReal real, imag;
    PetscScalar *values;
    PetscViewer viewer;
    Vec vector;
    PetscErrorCode ierr = PETSC_SUCCESS;
    // parse text
    ierr = ierr
        || PetscFOpen(PETSC_COMM_SELF, ctx->in, "r", &file)
        || user_is_ok(fscanf(file, "%d\n", &number), 1)
        || PetscMalloc2(number, &indices, number, &values);
    if (ctx->is_complex) {
        for (ith = 0; ith < number; ith++) {
            ierr = ierr || user_is_ok(fscanf(file, "%le %le\n", (double *)&real, (double *)&imag), 2);
            indices[ith] = ith;
            values[ith] = real + imag * PETSC_i;
        }
    } else {
        for (ith = 0; ith < number; ith++) {
            ierr = ierr || user_is_ok(fscanf(file, "%le\n", (double *)&values[ith]), 1);
            indices[ith] = ith;
        }
    }
    // setup vector
    ierr = ierr
        || VecCreate(PETSC_COMM_WORLD, &vector)
        || VecSetSizes(vector, PETSC_DECIDE, number)
        || VecSetType(vector, VECSEQ)
        || VecSetFromOptions(vector)
        || VecSetValues(vector, number, indices, values, INSERT_VALUES)
        || VecAssemblyBegin(vector)
        || VecAssemblyEnd(vector);
    // save binary
    if (ctx->flag_out) {
        ierr = ierr
            || PetscViewerBinaryOpen(PETSC_COMM_WORLD, ctx->out, FILE_MODE_WRITE, &viewer)
            || VecView(vector, viewer)
            || PetscViewerDestroy(&viewer);
    }
    if (ctx->is_stdout) {
        ierr = ierr || VecView(vector, PETSC_VIEWER_STDOUT_WORLD);
    }
    return ierr
        || VecDestroy(&vector)
        || PetscFree2(indices, values)
        || PetscFClose(PETSC_COMM_SELF, file);
}

PetscErrorCode user_save_matrix(AppCtx *ctx) {
    FILE *file;
    Mat matrix;
    PetscChar buffer[BUFFER_LENGTH], type[8];  // real or complex only
    PetscInt ith, num_rows, num_cols, row, col, number;
    PetscInt *rows, *cols, *row_nz;
    PetscReal real, imag;
    PetscScalar *values;
    PetscViewer viewer;
    PetscErrorCode ierr = PETSC_SUCCESS;
    // parse text
    ierr = ierr
        || PetscFOpen(PETSC_COMM_SELF, ctx->in, "r", &file)
        || user_is_ok(fscanf(file, "%%%%MatrixMarket matrix coordinate %s general\n", type), 1);
    for (;;) {
        ierr = ierr || user_is_ok(fscanf(file, "%[^\n]\n", buffer), 1);
        if (buffer[0] != '%') {
            break;
        }
    }
    ierr = ierr
        || user_is_ok(sscanf(buffer, "%d %d %d\n", &num_rows, &num_cols, &number), 3)
        || PetscMalloc3(number, &rows, number, &cols, number, &values)
        || PetscCalloc1(num_rows, &row_nz);
    if (ctx->is_complex || 0 == strcmp(type, "complex")) {
        for (ith = 0; ith < number; ith ++) {
            ierr = ierr || user_is_ok(fscanf(file, "%d %d %le %le\n", &row, &col, (double *)&real, (double *)&imag), 4);
            row -= ctx->base;
            rows[ith] = row;
            cols[ith] = col - ctx->base;
            values[ith] = real + imag * PETSC_i;
            row_nz[row]++;
        }
    } else {
        for (ith = 0; ith < number; ith ++) {
            ierr = ierr || user_is_ok(fscanf(file, "%d %d %le\n", &row, &col, (double *)&values[ith]), 3);
            row -= ctx->base;
            rows[ith] = row;
            cols[ith] = col - ctx->base;
            row_nz[row]++;
        }
    }
    // setup matrix
    ierr = ierr
        || MatCreate(PETSC_COMM_WORLD, &matrix)
        || MatSetSizes(matrix, PETSC_DECIDE, PETSC_DECIDE, num_rows, num_cols)
        || MatSetType(matrix, MATSEQAIJ)
        || MatSetFromOptions(matrix)
        || MatSeqAIJSetPreallocation(matrix, 0, row_nz);
    for (ith = 0; ith < number; ith++) {
        ierr = ierr || MatSetValues(matrix, 1, &rows[ith], 1, &cols[ith], &values[ith], INSERT_VALUES);
    }
    ierr = ierr
        || MatAssemblyBegin(matrix, MAT_FINAL_ASSEMBLY)
        || MatAssemblyEnd(matrix, MAT_FINAL_ASSEMBLY);
    // save binary
    if (ctx->flag_out) {
        ierr = ierr
            || PetscViewerBinaryOpen(PETSC_COMM_WORLD, ctx->out, FILE_MODE_WRITE, &viewer)
            || MatView(matrix, viewer)
            || PetscViewerDestroy(&viewer);
    }
    if (ctx->is_stdout) {
        ierr = ierr || MatView(matrix, PETSC_VIEWER_STDOUT_WORLD);
    }
    return ierr
        || MatDestroy(&matrix)
        || PetscFree4(rows, cols, row_nz, values)
        || PetscFClose(PETSC_COMM_SELF, file);
}
