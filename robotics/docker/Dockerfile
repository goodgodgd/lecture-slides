# 로봇공학 강의자료 검증용 환경 — Ubuntu 24.04 + ROS 2 Jazzy
#
# 호스트(우분투 22.04 서버)에는 ROS를 설치하지 않는다.
# 강의자료에 들어갈 명령어와 코드는 전부 이 컨테이너 안에서 돌려서 확인한다.
#
# 여기 적힌 설치 명령은 「ROS 2 설치」 회차 자료의 원본이기도 하다.
# 이미지 빌드가 성공하면 그 명령들이 실제로 동작한다는 증거가 된다.

FROM ubuntu:24.04

ARG DEBIAN_FRONTEND=noninteractive

# 1) 로캘 — ROS 2는 UTF-8 로캘을 요구한다
RUN apt-get update && apt-get install -y --no-install-recommends \
        locales curl gnupg ca-certificates software-properties-common \
    && locale-gen en_US en_US.UTF-8 \
    && update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8 \
    && rm -rf /var/lib/apt/lists/*
ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8

# 2) ROS 2 apt 저장소 등록 (universe 저장소가 먼저 켜져 있어야 한다)
RUN add-apt-repository universe \
    && curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
        -o /usr/share/keyrings/ros-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" \
        > /etc/apt/sources.list.d/ros2.list

# 3) ROS 2 Jazzy Desktop(RViz2 포함) + 개발 도구
#    ros-dev-tools 안에 colcon·rosdep·vcstool이 들어 있다.
RUN apt-get update && apt-get install -y --no-install-recommends \
        ros-jazzy-desktop \
        ros-dev-tools \
        build-essential cmake gdb git vim less \
    && rm -rf /var/lib/apt/lists/*

# 4) 셸을 열면 ROS 환경이 이미 잡혀 있게 한다
#    학생에게는 이 두 줄을 직접 .bashrc에 넣으라고 가르친다.
RUN echo 'source /opt/ros/jazzy/setup.bash' >> /home/ubuntu/.bashrc \
    && echo '[ -f /work/install/setup.bash ] && source /work/install/setup.bash' >> /home/ubuntu/.bashrc

# 5) UID 1000인 ubuntu 사용자로 돈다.
#    root로 돌리면 /work(호스트의 robotics/examples)에 root 소유 파일이 쌓여
#    호스트에서 편집할 수 없게 된다.
USER ubuntu
WORKDIR /work
CMD ["bash"]
