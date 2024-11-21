printf "Start of script\n"
set exec-wrapper env  'LD_PRELOAD=/projects/I20240002/andrelucena/trace-collector/build/libpadll.so'
set follow-fork-mode parent
run
bt