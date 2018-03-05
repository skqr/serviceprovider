#!/bin/sh

# Aptitude packages
apt-get update
apt-get install -y \
    git \
    zsh \
    htop \
    curl \
    vim \
    tmux \
    build-essential \
    libreadline-dev \
    libbz2-dev \
    libsqlite3-dev \
    libssl-dev \
    tk-dev \
    libpng-dev \
    libfreetype6-dev \
    libreadline6 \
    bzip2 \
    openssl \
    libncursesw5-dev
    # From line 12: Required by pyenv.

# Oh My Zsh plugins for .zshrc: (git debian python pyenv git-flow github lol nyan pip vagrant)
# TODO: Causes the error "chsh: PAM: Authentication failure"
# su vagrant -c "$(curl -fsSL https://raw.github.com/robbyrussell/oh-my-zsh/master/tools/install.sh)"
