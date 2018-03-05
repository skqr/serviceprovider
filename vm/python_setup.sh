#!/bin/sh

VAGRANT_HOME="/home/vagrant"
PYENV_FILE="$VAGRANT_HOME/.pyenv_init"
PYTHON_VERSION="3.6.1"

# Install in Bash and Zsh
su vagrant -c "curl -L https://raw.githubusercontent.com/pyenv/pyenv-installer/master/bin/pyenv-installer | bash"
su vagrant -c "curl -L https://raw.githubusercontent.com/pyenv/pyenv-installer/master/bin/pyenv-installer | zsh"

# Compose init script
PYENV_SCRIPT="export PATH=\"$VAGRANT_HOME/.pyenv/bin:$PATH\"; eval \"\$(pyenv init -)\"; eval \"\$(pyenv virtualenv-init -)\""
echo "$PYENV_SCRIPT" > $PYENV_FILE

# Add to shell profile
echo "source $PYENV_FILE" >> $VAGRANT_HOME/.bashrc
echo "source $PYENV_FILE" >> $VAGRANT_HOME/.zshrc

# Install Python
su vagrant -c "$PYENV_SCRIPT; \$(pyenv install $PYTHON_VERSION)"
su vagrant -c "$PYENV_SCRIPT; \$(pyenv global $PYTHON_VERSION)"

# Pip packages
su vagrant -c "$PYENV_SCRIPT; pip install --upgrade pip"
su vagrant -c "$PYENV_SCRIPT; pip install --upgrade -r /vagrant/requirements.txt"
