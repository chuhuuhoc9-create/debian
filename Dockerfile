FROM debian:bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    TZ=Asia/Ho_Chi_Minh \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

RUN dpkg --add-architecture i386

RUN apt-get update && apt-get install -y --no-install-recommends \
    xrdp \
    xorg \
    xorgxrdp \
    xfce4 \
    xfce4-goodies \
    dbus \
    dbus-x11 \
    policykit-1 \
    sudo \
    curl \
    wget \
    nano \
    vim-tiny \
    net-tools \
    iproute2 \
    procps \
    psmisc \
    ca-certificates \
    pulseaudio \
    pulseaudio-utils \
    pulseaudio-module-x11 \
    firefox-esr \
    wine \
    wine32 \
    wine64 \
    winbind \
    cabextract \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ARG USERNAME=xrdpuser
ARG USER_UID=1000
ARG USER_GID=1000
ARG USER_PASSWORD=xrdp

RUN groupadd --gid ${USER_GID} ${USERNAME} \
    && useradd --uid ${USER_UID} --gid ${USER_GID} --create-home --shell /bin/bash ${USERNAME} \
    && echo "${USERNAME}:${USER_PASSWORD}" | chpasswd \
    && usermod -aG sudo,audio,video,ssl-cert ${USERNAME} \
    && echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/${USERNAME} \
    && chmod 0440 /etc/sudoers.d/${USERNAME}

RUN printf '%s\n' \
    '#!/bin/sh' \
    'unset DBUS_SESSION_BUS_ADDRESS' \
    'unset XDG_RUNTIME_DIR' \
    'exec dbus-launch --exit-with-session startxfce4' \
    > /home/${USERNAME}/.xsession \
    && chown ${USERNAME}:${USERNAME} /home/${USERNAME}/.xsession \
    && chmod 700 /home/${USERNAME}/.xsession

RUN sed -i 's/^allowed_users=.*/allowed_users=anybody/' /etc/X11/Xwrapper.config || \
    echo 'allowed_users=anybody' >> /etc/X11/Xwrapper.config

RUN adduser xrdp ssl-cert

RUN printf '%s\n' \
    '#!/bin/sh' \
    '[ -r /etc/profile ] && . /etc/profile' \
    '[ -r "$HOME/.profile" ] && . "$HOME/.profile"' \
    'export LANG=C.UTF-8' \
    'export LC_ALL=C.UTF-8' \
    'export XDG_CURRENT_DESKTOP=XFCE' \
    'exec dbus-launch --exit-with-session startxfce4' \
    > /etc/xrdp/startwm.sh \
    && chmod +x /etc/xrdp/startwm.sh

COPY start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 3389

CMD ["/start.sh"]
