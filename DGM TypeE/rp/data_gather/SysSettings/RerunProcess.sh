#!/bin/bash

clear

while :
do
  ProcNumber=`ps -ef | grep 'process.py' | grep -v 'grep' | wc -l`
  echo "$ProcNumber"
  if [ $ProcNumber -eq 0 ];then
	python3 /home/rp/.data_gather/Core/process.pyc &
  fi
  sleep 30
done
