#!/bin/bash

grep -q "^PASS_MIN_DAYS" {{{ login_defs_path }}} && \
  sed -i "s/PASS_MIN_DAYS.*/# PASS_MIN_DAYS\t1/g" {{{ login_defs_path }}}
if ! [ $? -eq 0 ]; then
    echo -e "# PASS_MIN_DAYS\t1" >> {{{ login_defs_path }}}
fi
