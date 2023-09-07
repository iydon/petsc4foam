ARG VERSION_UBUNTU=20.04

FROM ubuntu:${VERSION_UBUNTU}

ARG DEBIAN_FRONTEND=noninteractive
# https://github.com/microsoft/vscode-cmake-tools
ARG VERSION_CMAKETOOLS=1.14.30
# https://github.com/microsoft/vscode-cpptools
ARG VERSION_CPPTOOLS=1.14.5
ARG VERSION_OPENFOAM=2012

SHELL ["/bin/bash", "-c"]

WORKDIR /usr/lib/openfoam/

# OpenFOAM.com
RUN sed -i 's@//.*archive.ubuntu.com@//mirrors.ustc.edu.cn@g' /etc/apt/sources.list && \
    apt-get update && \
    apt-get -y install --no-install-recommends curl ca-certificates && \
    curl -fsSL https://dl.openfoam.com/add-debian-repo.sh | bash && \
    apt-get update && \
    apt-get -y install --no-install-recommends openfoam${VERSION_OPENFOAM}-default

# PETSc4FOAM
RUN apt-get -y install --no-install-recommends git python3-dev wget && \
    cd openfoam${VERSION_OPENFOAM} && \
    source etc/bashrc && \
    source etc/config.sh/petsc && \
    rm --force $WM_THIRD_PARTY_DIR && \
    git clone https://develop.openfoam.com/Development/ThirdParty-common $WM_THIRD_PARTY_DIR && \
    cd $WM_THIRD_PARTY_DIR && \
    wget https://ftp.mcs.anl.gov/pub/petsc/release-snapshots/$petsc_version.tar.gz && \
    tar xzf $petsc_version.tar.gz && \
    ./makePETSC -- --download-f2cblaslapack=1 && \
    git clone https://develop.openfoam.com/modules/external-solver $WM_THIRD_PARTY_DIR/external-solver && \
    cd $WM_THIRD_PARTY_DIR/external-solver && \
    ./Allwmake -j 1>stdout.log 2>stderr.log

# code-server: source ... && PASSWORD=password code-server --bind-addr=0.0.0.0:7101 1>stdout.log 2>stderr.log &
# RUN apt-get -y install --no-install-recommends build-essential cmake gdb && \
#     cd /tmp/ && \
#     curl -fsSL https://code-server.dev/install.sh | bash && \
#     wget https://github.com/microsoft/vscode-cmake-tools/releases/download/v${VERSION_CMAKETOOLS}/cmake-tools.vsix && \
#     wget https://github.com/microsoft/vscode-cpptools/releases/download/v${VERSION_CPPTOOLS}/cpptools-linux.vsix && \
#     code-server --install-extension cpptools-linux.vsix --install-extension cmake-tools.vsix

# ParaView: pvserver --server-port=7102
# RUN apt-get -y install --no-install-recommends paraview
