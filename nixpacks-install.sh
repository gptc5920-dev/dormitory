#!/bin/sh
set -eu

python -m venv --copies /opt/venv
. /opt/venv/bin/activate

# Use the Apt headers and compiler together; Nix pkg-config may omit system paths.
export PKG_CONFIG_LIBDIR="/usr/lib/$(/usr/bin/gcc -dumpmachine)/pkgconfig:/usr/share/pkgconfig"
/usr/bin/pkg-config --exists libmariadb
MYSQLCLIENT_CFLAGS="$(/usr/bin/pkg-config --cflags libmariadb)"
MYSQLCLIENT_LDFLAGS="$(/usr/bin/pkg-config --libs libmariadb)"
export MYSQLCLIENT_CFLAGS MYSQLCLIENT_LDFLAGS
export CC=/usr/bin/gcc

python -m pip install --index-url https://download.pytorch.org/whl/cpu torch torchvision
python -m pip install -r requirements.txt
python -m pip check
