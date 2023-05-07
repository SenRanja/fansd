#!/bin/bash

PROC_PATH="/root/fansd/"
PROC_NAME="fansd.py"
RUN_PROC_COMMAND="/usr/bin/python3 ${PROC_NAME}"
MAINPID=`ps -ef | grep ${PROC_NAME} | grep -v grep`

# check main program status

if [ ! "$MAINPID" ]; then
        # start program
        cd ${PROC_PATH}
        #echo ${RUN_PROC_COMMAND}
        $RUN_PROC_COMMAND
fi

echo "${PROC_NAME} start up"
