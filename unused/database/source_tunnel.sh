#!/bin/bash

#for pymongo db support
check_tunnel (){
    ps aux | grep "ssh -f -L 37017:localhost:27017" | grep fact >/dev/null
}
if ! check_tunnel ; then
    ./make_tunnel.sh
fi