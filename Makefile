MAKE = make
PYTHON = python3


.PHONY: help \
	openfoamcom-or-openfoamorg \
	test-for-petsc4foam \
	suite_sparse foam2mtx data_labeling


help:                        ## Print the usage
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e "s/\\$$//" | sed -e "s/##//"

openfoamcom-or-openfoamorg:  ## OpenFOAM.com or OpenFOAM.org
	@cd part/$@/ && \
		$(MAKE)

test-for-petsc4foam:         ## Test for PETSc4FOAM
	@cd part/$@/default/ && \
		$(PYTHON) main.py
	@cd part/$@/tuning/ && \
		$(PYTHON) main.py

suite_sparse:                ## Hyper-parameter Optimization :: Training Dataset :: suite_sparse
	@cd part/hyper-parameter-optimization/training-dataset/ && \
		$(PYTHON) -m $@ init && \
		$(PYTHON) -m $@ spy --shape 512

foam2mtx:                    ## Hyper-parameter Optimization :: Training Dataset :: foam2mtx
	@cd part/hyper-parameter-optimization/training-dataset/$@/ && \
		$(PYTHON) script/tutorial.py && \
		$(PYTHON) script/mtx.py && \
		$(PYTHON) script/spy.py

data_labeling:               ## Hyper-parameter Optimization :: Training Dataset :: data_labeling
	@cd part/hyper-parameter-optimization/training-dataset/$@/src/ && \
		$(MAKE) install
	@cd part/hyper-parameter-optimization/training-dataset/$@/ && \
		$(PYTHON) main.py
