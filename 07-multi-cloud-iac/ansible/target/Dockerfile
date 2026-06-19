FROM ubuntu:22.04

# Install SSH, sudo, and python3 (required for Ansible)
RUN apt-get update && apt-get install -y \
    openssh-server \
    sudo \
    python3 \
    python3-pip \
    curl \
    iproute2 \
    systemd \
    systemd-sysv \
    && rm -rf /var/lib/apt/lists/*

# Configure SSH daemon
RUN mkdir /var/run/sshd
RUN echo 'root:rootpassword' | chpasswd

# Setup SSH key directory
RUN mkdir -p /root/.ssh && chmod 700 /root/.ssh

# Copy the public key to authorized_keys
COPY id_rsa.pub /root/.ssh/authorized_keys
RUN chmod 600 /root/.ssh/authorized_keys

RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config

# SSH login fix. Otherwise user is kicked off after login
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd

ENV NOTVISIBLE "in users profile"
RUN echo "export VISIBLE=now" >> /etc/profile

EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"]
