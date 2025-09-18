#!/bin/bash

set -euo pipefail

#
# Script to deploy fms_yaml_tools on C5
#
# The $n most recent tags (where $n is set at the top of the script) are deployed
# to the directory above the Git repo's base dir. If the tag is already deployed,
# and broken symlinks are found in its bin directory, then its virtual environment
# will be rebuilt.
#
# Usage:
# ./deploy.sh
#

# Number of tags (the $n most recent) to deploy
n=3

# Fetch updates
git fetch

repo_basedir=`git rev-parse --show-toplevel`
tags=`git tag --sort=-committerdate | head -n $n`

for tag in $tags
do
  venv_dir=$repo_basedir/../$tag

  # Check if a directory for this tag already exists
  if [ -d $venv_dir ]
  then
    # Check if the bin directory contains any broken symlinks
    if [ -d $venv_dir/bin ] && [ -z "`find -L $venv_dir/bin -type l -print -quit`" ]
    then
      echo "$tag exists with intact symlink: skipping"
      continue
    else
      echo "$tag exists with broken symlink: rebuilding"
      rm -rf $venv_dir
    fi
  else
    echo "Installing $tag"
  fi

  # Checkout this tag
  git checkout $tag

  # Create the venv
  mkdir $venv_dir
  python3 -m venv $venv_dir

  # Install fms_yaml_tools and its dependencies to the venv
  source $venv_dir/bin/activate
  pip3 install --upgrade pip setuptools
  pip3 install $repo_basedir

  # Workaround for Python issue #82066 (unbound variable in `deactivate`)
  set +u
  deactivate
  set -u
done
