#!/bin/bash

################################################################################
# Resonance Project                                                            #
# Resonance implemented with Pyretic platform                                  #
# author: Muhammad Shahbaz (muhammad.shahbaz@gatech.edu)                       #
################################################################################
 
case "$1" in
   enable)
      echo "Enabling sFlow ..." 
      ovs-vsctl -- --id=@sflow create sflow agent=eth3 target=\"127.0.0.1:6343\" \
      sampling=2 polling=20 -- -- set bridge $2 sflow=@sflow
   ;;
   disable)
      echo "Disabling sFlow ..."  	
	  ovs-vsctl -- clear bridge $2 sflow
   ;;
   *)
      echo "Usage: mn-sflow.sh {enable|disable} {switch-id}"
   ;;
esac
