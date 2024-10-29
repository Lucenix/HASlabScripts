#!/bin/bash

tools=()

for file in bpftrace-tools/*; do 
    if [ -f "$file" ]; then 
        tools+=( "$(basename "$file" .bt)" )
    fi 
done

start_tools() {
    # check if outputs directory exists
    if [ ! -d "outputs" ]; then
        mkdir -p outputs
    else
      # ask user if they want to delete the existing outputs
      read -p "Outputs directory already exists. Do you want to delete the existing outputs? (y/n): " delete_outputs
      if [ "$delete_outputs" == "y" ]; then
        rm -rf outputs
        mkdir -p outputs
      fi
    fi

    mkdir -p outputs
    mkdir -p pids
	shift 1
    for tool in "${tools[@]}"
    do
        tool_executable="tools/$tool.bt"
        sudo bpftrace $tool_executable > outputs/$tool 2>&1 &
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

  rm -r pids/
}

if [ "$1" == "start" ]; then
    start_tools
elif [ "$1" == "stop" ]; then
    stop_tools
else
    echo "Usage: $0 start|stop"
fi
