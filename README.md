<div align="center">
  <a href="https://github.com/iydon/petsc4foam">
    🟢⬜🟩⬜🟩<br />
    ⬜⬜⬜⬜⬜<br />
    🟩⬜🟩⬜🟩<br />
    ⬜⬜⬜⬜⬜<br />
    🟩⬜🟩⬜🟩<br />
  </a>

  <h3 align="center">PETSc4FOAM</h3>

  <p align="center">
    Speed Up OpenFOAM Framework with PETSc Library (experimental)
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#openfoamcom-or-openfoamorg">OpenFOAM.com or OpenFOAM.org</a></li>
    <li><a href="#solution-for-managing-petsc-installations">Solution for Managing PETSc Installations</a></li>
    <li><a href="#references">References</a></li>
  </ol>
</details>



## OpenFOAM.com or OpenFOAM.org

There are two major distributions of OpenFOAM[^1]: OpenFOAM.com (ESI-OpenCFD) and OpenFOAM.org (OpenFOAM Foundation). In order to avoid compatibility issues, we need to compare the two distributions and choose the one with the more stable API.

OpenFOAM is compiled using a customized tool named wmake, which is a further wrapper around the compilation tool Make. It can be said that wmake has a narrower scope of use, and thus is less adaptable to mainstream toolchains. Therefore, it is cumbersome to analyze OpenFOAM API compatibility at the source code level, so we currently use tutorial compatibility to reflect OpenFOAM API compatibility.

Tutorial compatibility is based on the number of lines, we use $n_0$ for the number of lines in the original file, $n_a$ for the number of lines added, and $n_d$ for the number of lines deleted, so the tutorial compatibility $C_t$ has the following formula, which is between 0 and 1, and the smaller the value, the better the compatibility.

$$
C_t = \frac{n_a + n_d}{2n_0 + n_a - n_d}
$$

Figures [1](#figure-1.1) and [2](#figure-1.2) represent the distribution of tutorial compatibility between different versions of OpenFOAM, with the horizontal coordinate representing the different versions of OpenFOAM and the vertical coordinate representing the tutorial compatibility[^2]. It can be seen that the tutorial compatibility of OpenFOAM.com is better than that of OpenFOAM.org, and therefore we use OpenFOAM.com to avoid compatibility issues as much as possible.

<figure id="figure-1.1">
  <img id="figure-1.1" src="part/openfoamcom-or-openfoamorg/static/figure/com.jpg" />
  <figcaption>Figure 1.1: OpenFOAM.com</figcaption>
</figure>

<figure id="figure-1.2">
  <img id="figure-1.2" src="part/openfoamcom-or-openfoamorg/static/figure/org.jpg" />
  <figcaption>Figure 1.2: OpenFOAM.org</figcaption>
</figure>



## Solution for Managing PETSc Installations[^3][^4]

Some matrices contain complex numbers, and the PETSc library needs to modify configuration options to conditionally compile a version that supports real or complex numbers; at the same time, local debugging needs to disable the optimization flag to compile a version that contains debuggable code, while HPC needs to enable the optimization flag to speed up the target code.

The installation management in the PETSc official document is relatively simple, and each switch needs to specify a number of environment variables, which makes the operation more cumbersome; at the same time, the PETSc application code compilation relies too much on Make, and basically all the compile flags and search paths are stored in the form of variables in Make, which is not conducive to switching to CMake and other standard and modern code build systems, and thus we need to implement function jumps and other functions in the local IDE.

We use Python to merge the installation management steps in the official PETSc documentation, and by presetting a number of configuration options, we realize that a single command completes the installation, configuration and other cumbersome operations, which reduces the burden on the mind.

```shell
$ ipetsc build \
    --arch advance-real-optimize \
    --arch advance-complex-optimize

$ source etc/bashrc.advance-real-optimize.sh
$ echo $PETSC_ARCH
advance-real-optimize

$ source etc/bashrc.advance-complex-optimize.sh
$ echo $PETSC_ARCH
advance-complex-optimize
```

In addition to the preset configuration options, users can also add customized configuration options to increase the flexibility of our solution. Finally, we refer to OpenFOAM's use of etc/bashrc to store compile flags and search paths as environment variables, thus allowing us to switch between different code build systems at will.

```shell
$ BASE=basic-real-optimize
$ ipetsc build \
    --arch $BASE:$BASE-amgx \
    -- \
    --download-triangle=1 \
    --download-amgx=1 \
    --download-amgx-cmake-arguments="-DMPI_CXX_COMPILE_DEFINITIONS=-lmpi" \
    --with-cuda-dir=/usr/local/cuda/
```

Moreover, it is possible to add extra features to our solution, such as:

- Visualizing sparse matrices to visually display the non-zero element distribution of the matrices, thus narrowing down the range of hyper-parameters of the solving algorithm;
- Analyzing LogView and thus quantifying the performance of the PETSc application code in order to compare different hyper-parameters of the solving algorithm;
- Generating PETSc application code templates, or configuration files for the code build systems (CMakeLists.txt, etc.).

```shell
$ ipetsc cvt \
    --input data/1/A.mtx \
    --output cache/data/1/A.npz \
    --type real --base 0

$ ipetsc spy \
    --input data/1/A.mtx \
    --output image/1.png \
    --size 1024x1024

$ ipetsc new \
    --path src/prob_real/ \
    --update  # Update cmake, makefile, vscode
$ ls --all src/prob_real/
.  ..  CMakeLists.txt  main.c  Makefile  .vscode
```



## References

[^1]: https://www.cfd-online.com/Forums/openfoam/197150-openfoam-com-versus-openfoam-org-version-use.html
[^2]: https://seaborn.pydata.org/generated/seaborn.boxenplot.html
[^3]: https://gitlab.com/Iydon/solver_challenge
[^4]: https://github.com/iydon/iPETSc
