#!/bin/bash

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
	OUTPUT=../../../statistics/eBPFs_subset/eBPF_output_$1
	mkdir -p "$OUTPUT"
    mkdir -p pids
	echo $(pwd)
    for tool in "${tools[@]}"
    do
        tool_executable="bpftrace-tools/$tool.bt"
        sudo bpftrace $tool_executable > "$OUTPUT/$tool" 2>&1 &
        echo $! > pids/$tool.pid
        echo "Started $tool (pid: $!)"
    done

	for tool in "${libbpf_tools[@]}"
	do
        tool_executable="libbpf-tools/$tool.bt"
        sudo $tool_executable > "$OUTPUT/$tool" 2>&1 &
        echo $! > pids/$tool.pid
        echo "Started $tool (pid: $!)"
    done
}

stop_tools() {
  for tool in "${tools[@]}"
  do
    pid=$(cat pids/$tool.pid)
    echo "Stopping $tool (pid: $pid)"
    sudo kill -SIGTERM $pid
  done

  echo "Waiting for tools to stop..."
  for tool in "${tools[@]}"
  do
    pid=$(cat pids/$tool.pid)
    tail --pid=$pid -f /dev/null
    echo "Stopped $tool"
  done
	
  echo ${libbpf_tools[@]}
  for tool in "${libbpf_tools}"
  do
	pid=$(cat pids/$tool.pid)
	tail --pid=$pid -f /dev/null
	echo "Stopped $tool (libbpf)"		
  done

  rm -r pids/
}

if [ "$1" == "start" ]; then
	if [ -z "$2" ]
		then 
			start_tools default
		else
			start_tools $2
	fi
elif [ "$1" == "stop" ]; then
    stop_tools
else
    echo "Usage: $0 start|stop"
fi
