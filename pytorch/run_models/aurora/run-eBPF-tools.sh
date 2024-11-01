#!/bin/bash

tools=()
for file in tools/*; do 
    if [ -f "$file" ]; then 
        tools+=( "$(basename "$file")" )
    fi 
done

start_tools() {
	OUTPUT=$1
    mkdir -p $OUTPUT/pids
	echo $(pwd)
    for tool in "${tools[@]}"
    do
        tool_executable="tools/$tool"
        screen -S $tool -d -m -L -Logfile $OUTPUT/$tool bash -c "sudo $tool_executable"
        pid=$(screen -ls | awk "/\.$tool\t/ {print strtonum(\$1)}")
        echo $pid > $OUTPUT/pids/$tool.pid
        echo "Started $tool (pid: $pid)"
    done
}

stop_tools() {
  OUTPUT=$1
  
  for tool in "${tools[@]}"
  do
    pid=$(cat $OUTPUT/pids/$tool.pid)
    echo "Stopping $tool (pid: $pid)"
    screen -X -S $tool stuff "^C"
  done

  echo "Waiting for tools to stop..."
  for tool in "${tools[@]}"
  do
	pid=$(cat $OUTPUT/pids/$tool.pid)
    tail --pid=$pid -f /dev/null
    echo "Stopped $tool"
  done

  rm -r $OUTPUT/pids/
}

if [ "$1" == "start" ]; then
	if [ -z "$2" ]
		then 
			start_tools ./default
		else
			start_tools $2
	fi
elif [ "$1" == "stop" ]; then
    if [ -z "$2" ]
        then
            stop_tools ./default
        else
            stop_tools $2
    fi
else
    echo "Usage: $0 start|stop [OUTPUT_PATH]"
fi
