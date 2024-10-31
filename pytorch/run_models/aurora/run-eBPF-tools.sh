#!/bin/sh

tools=()
libbpf_tools=()

for file in bpftrace-tools/*; do 
    if [ -f "$file" ]; then 
        tools+=( "$(basename "$file" .bt)" )
    fi 
done

for file in libbpf-tools/*; do 
    if [ -f "$file" ]; then 
        libbpf_tools+=( "$(basename "$file")" )
    fi 
done

start_tools() {
    rm -rf $1
	OUTPUT=$1
	mkdir -p "$OUTPUT"
    mkdir -p $OUTPUT/pids
	echo $(pwd)
    for tool in "${tools[@]}"
    do
        tool_executable="bpftrace-tools/$tool.bt"
        screen -S $tool -d -m bash -c "sudo bpftrace $tool_executable > $OUTPUT/$tool 2>&1"
        pid=$(screen -ls | awk "/\.$tool\t/ {print strtonum(\$1)}")
        echo $pid > $OUTPUT/pids/$tool.pid
        echo "Started $tool (pid: $pid)"
    done

	for tool in "${libbpf_tools[@]}"
	do
#-L -Logfile $OUTPUT/$tool 
        tool_executable="libbpf-tools/$tool"
		screen -S $tool -d -m bash -c "sudo $tool_executable"
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
  
  for tool in "${libbpf_tools}"
   do
	screen -X -S $tool stuff "^C"
	pid=$(pgrep -u root $tool)
	sudo kill $pid
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
    echo "Usage: $0 start|stop"
fi
