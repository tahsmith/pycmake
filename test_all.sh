#!/usr/bin/env bash

FAIL_COUNT=0
COUNT=0
for F in `find $1 -name CMakeLists.txt` `find $1 -name "*.cmake"`
do
    # Was it supposed to fail? Look for error log. If so, don't include it in our logs
    root=${F%.cmake}
    if [ ! -e ${root}-stderr.txt ]; then
        python cmake.py ${F}
        if [ $? -ne 0 ]; then
            let FAIL_COUNT+=1
        fi
        let COUNT+=1
    fi
done

echo TOTALS:  ${COUNT} tests, ${FAIL_COUNT} failed.