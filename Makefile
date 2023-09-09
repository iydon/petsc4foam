MAKE = make
PYTHON = python3


.PHONY: help openfoamcom-or-openfoamorg test-for-petsc4foam hyper-parameter-optimization


help:                          ## Print the usage
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e "s/\\$$//" | sed -e "s/##//"

openfoamcom-or-openfoamorg:    ## OpenFOAM.com or OpenFOAM.org
	@cd part/$@/ && \
		$(MAKE)

test-for-petsc4foam:           ## Test for PETSc4FOAM
	@cd part/$@/default/ && \
		$(PYTHON) main.py
	@cd part/$@/tuning/ && \
		$(PYTHON) main.py

hyper-parameter-optimization:  ## Hyper-parameter Optimization
	@cd part/$@/training-dataset/ && \
		$(PYTHON) -m suite_sparse init && \
		$(PYTHON) -m suite_sparse spy --shape 512
	@cd part/$@/training-dataset/foam2mtx/ && \
		$(PYTHON) script/tutorial.py && \
		$(PYTHON) script/mtx.py && \
		$(PYTHON) script/spy.py
