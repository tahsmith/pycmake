#!/usr/bin/env bash

for D in `find $1 -type d`
do
    python cmake.py ${D}/CMakeLists.txt
done