#!/bin/bash
mkdir -p /cache/root_{work,upper}
fuse-overlayfs -o lowerdir=/root,upperdir=/cache/root_upper,workdir=/cache/root_work /root
