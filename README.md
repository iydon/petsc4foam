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
    <li><a href="#references">References</a></li>
  </ol>
</details>



## OpenFOAM.com or OpenFOAM.org

There are two major distributions of OpenFOAM[^1]: OpenFOAM.com (ESI-OpenCFD) and OpenFOAM.org (OpenFOAM Foundation). In order to avoid compatibility issues, we need to compare the two distributions and choose the one with the more stable API.

OpenFOAM is compiled using a customized tool named `wmake`, which is a further packaging of the compilation tool `make`. It can be said that `wmake` has a narrower scope of use, and thus is less adaptable to mainstream toolchains. Therefore, it is cumbersome to analyze OpenFOAM API compatibility at the source code level, so we currently use tutorial compatibility to reflect OpenFOAM API compatibility.

Tutorial compatibility is based on the number of lines, we use $n_0$ for the number of lines in the original file, $n_a$ for the number of lines added, and $n_d$ for the number of lines deleted, so the tutorial compatibility $C_t$ has the following formula, which is between 0 and 1, and the smaller the value, the better the compatibility.

$$
C_t = \frac{n_a + n_d}{2n_0 + n_a - n_d}
$$

Figures [1](#figure-1.1) and [2](#figure-1.2) represent the distribution of tutorial compatibility between different versions of OpenFOAM, with the horizontal coordinate representing the different versions of OpenFOAM and the vertical coordinate representing the tutorial compatibility[^2]. It can be seen that the tutorial compatibility of OpenFOAM.com is better than that of OpenFOAM.org, and therefore we use OpenFOAM.com to avoid compatibility issues as much as possible.

<figure id="figure-1.1">
  <img src="part/openfoamcom-or-openfoamorg/static/figure/com.jpg" />
  <figcaption>Figure 1.1: OpenFOAM.com</figcaption>
</figure>

<figure id="figure-1.2">
  <img src="part/openfoamcom-or-openfoamorg/static/figure/org.jpg" />
  <figcaption>Figure 1.2: OpenFOAM.org</figcaption>
</figure>



## References

[^1]: https://www.cfd-online.com/Forums/openfoam/197150-openfoam-com-versus-openfoam-org-version-use.html
[^2]: https://seaborn.pydata.org/generated/seaborn.boxenplot.html
