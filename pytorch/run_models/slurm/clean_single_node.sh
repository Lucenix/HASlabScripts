#!/bin/sh
# Join process
# --$1: process identifier

module load ncurses/6.3

join_process() 
{
        echo "utils::join_process"
        $SCREEN_PATH -X -S $1 stuff "^C"
}

join_process dstat
join_process nvidia