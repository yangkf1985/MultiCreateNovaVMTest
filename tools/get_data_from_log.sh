#!/usr/bin/env bash
cat /var/log/TestNovaCase/test_nova_case.log | grep 'create_server' | grep 'start' |awk '{print $8,$11}' > create_server_start.txt
cat /var/log/TestNovaCase/test_nova_case.log | grep 'create_server' | grep 'end' |awk '{print $8,$11,$14}' > create_server_end.txt
cat /var/log/TestNovaCase/test_nova_case.log | grep 'get_server' | grep 'start' |awk '{print $8,$11}' > get_server_start.txt
cat /var/log/TestNovaCase/test_nova_case.log | grep 'get_server' | grep 'end' |awk '{print $8,$11,$14}' > get_server_end.txt