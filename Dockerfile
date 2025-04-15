# Choose a base nvidia image
FROM nvidia/cuda:12.5.1-cudnn-devel-ubuntu22.04
ARG user_name=user1
ARG n_jobs=4

# Non-interactive installation mode
ENV DEBIAN_FRONTEND=noninteractive

# Set the locale
RUN apt update && \
    apt install -y -qq locales && \
    locale-gen en_US en_US.UTF-8 && \
    update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
ENV LANG=en_US.UTF-8

# Install essentials
RUN apt-get update && apt-get install -y apt-utils \
    software-properties-common sudo psmisc lsb-release \
    protobuf-compiler libatlas-base-dev tmux nano geany \
    vim wget curl build-essential git cmake cmake-curses-gui \
    autoconf xserver-xorg-video-dummy xserver-xorg-legacy \
    net-tools terminator libjpeg-dev ffmpeg apt-transport-https \
    ca-certificates gnupg locales \
    curl zip unzip tar \
    bash-completion && \
    rm -rf /var/lib/apt/lists/*

# Create user: ${user_name}
USER root
RUN useradd -l -u 33334 -G sudo -md /home/${user_name} -s /bin/bash -p ${user_name} ${user_name} && \
    # passwordless sudo for users in the 'sudo' group
    sed -i.bkp -e 's/%sudo\s\+ALL=(ALL\(:ALL\)\?)\s\+ALL/%sudo ALL=NOPASSWD:ALL/g' /etc/sudoers

USER ${user_name}
WORKDIR /home/${user_name}

# Install miniforge
RUN wget "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
RUN /bin/bash -c "bash /home/${user_name}/Miniforge3-$(uname)-$(uname -m).sh -b -p /home/${user_name}/miniforge3"
RUN /home/${user_name}/miniforge3/bin/conda init

# Copy the environment file
COPY envs/yarp_environment.yml .

RUN /bin/bash -c "source /home/${user_name}/miniforge3/etc/profile.d/conda.sh && \
    conda env create -f environment_production.yml && \
    conda clean -afy"

ENV PATH=${PATH}:/home/${user_name}/miniforge3/bin
# Make RUN commands use the new environment:
SHELL ["conda", "run", "-n", "fcl_prod", "/bin/bash", "-c"]

# Clone the superbuild
RUN git clone https://github.com/robotology/robotology-superbuild.git && \
    cd robotology-superbuild && \
    mkdir build && cd build && \
    git config --global user.name iit && \
    git config --global user.email "empty@iit.it"&& \
    cmake -DROBOTOLOGY_USES_PYTHON=ON .. && \
    source ./install/share/robotology-superbuild/setup.sh && \
    make -j${n_jobs}

RUN echo "conda activate fcl_prod" >> ~/.bashrc
RUN echo "source /home/user1/robotology-superbuild/build/install/share/robotology-superbuild/setup.sh" >> ~/.bashrc

RUN git clone https://github.com/hsp-iit/few-shot-console.git

