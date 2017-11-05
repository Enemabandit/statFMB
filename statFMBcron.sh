#!/bin/bash

case "$(pidof -x statFMB | wc -w)" in
    0) echo "Restarting statFMB: $(date)" >> /var/log/statFMBcrond.txt
 # run code here
       ./venv/bin/statFMB >> /var/log/statFMBout.txt
       ;;
    1) echo "OK: $(date)" >> /var/log/statFMBcrond.txt
       ;;
    *) echo "Removed double statFMB: $(date)" >> /var/log/statFMB.crond.txt
       kill $(pidof -x statFMB | awk '{print $1}')
       ;;
esac
