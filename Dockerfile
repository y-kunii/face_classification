#Busterでなく、stretchのImageベース
FROM raspbian/stretch:latest

LABEL version="7.0"
LABEL description="EmotionFlower"

RUN apt-get update

#必要なものInstall
RUN apt-get install -y vim
RUN apt install -y iputils-ping net-tools
RUN apt install -y x11-apps
RUN apt-get install -y python3 python3-pip

#SSH設定
RUN apt install -y openssh-server
RUN sed -i -e "s/#Port 22/Port 5022"/g /etc/ssh/sshd_config
RUN service ssh restart

ARG wkdir=/home/work
WORKDIR ${wkdir}

#OpenCV
RUN wget https://github.com/mt08xx/files/raw/master/opencv-rpi/libopencv3_3.4.0-20180115.1_armhf.deb
RUN apt install -y ./libopencv3_3.4.0-20180115.1_armhf.deb
RUN ldconfig

#Tensorflow系
RUN apt install -y libblas-dev liblapack-dev python3-dev libatlas-base-dev gfortran python3-setuptools
RUN apt install -y python3-h5py python3-pandas

#git
RUN apt install -y git

#User追加
ARG USERNAME=emotion
ARG GROUPNAME=emotion
ARG UID=1000
ARG GID=1000
ARG PASSWORD=emotion
RUN groupadd -g $GID $GROUPNAME && \
    useradd -m -s /bin/bash -u $UID -g $GID -G sudo $USERNAME && \
    echo $USERNAME:$PASSWORD | chpasswd && \
    echo "$USERNAME   ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
USER $USERNAME:$GROUPNAME
RUN whoami
WORKDIR /home/$USERNAME/

#pip系
RUN pip3 install numpy==1.16.4
RUN pip3 install https://github.com/lhelontra/tensorflow-on-arm/releases/download/v1.4.1/tensorflow-1.4.1-cp35-none-linux_armv7l.whl
RUN pip3 install matplotlib==3.0.3
RUN pip3 install scipy==1.3.0
RUN pip3 install keras==2.1.3
RUN pip3 install imageio==2.9.0
RUN pip3 install pyserial==3.5
RUN pip3 install requests

#Tensorflow lite
RUN pip3 install https://github.com/google-coral/pycoral/releases/download/release-frogfish/tflite_runtime-2.5.0-cp35-cp35m-linux_armv7l.whl

ENV PYTHONIOENCODING="utf-8"

