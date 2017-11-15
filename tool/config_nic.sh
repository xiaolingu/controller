# author: gxl
#!/bin/bash
password="123456"
exec_file="../client"
if [ -e $exec_file ]; then
    echo $password | sudo -S setcap cap_net_raw,cap_net_admin=eip ${exec_file}
    echo "set cap_net_admin sucessfully..."
else
    echo "Warning: ${exec_file} isn't exist..."
    exit 1
fi
var=`ifconfig | grep "Link encap" | awk '{print $1}' | grep 'wlan'`
if [ [${var} == ' '] ];then
    echo "Warning: ${var} isn't exist ..."
    exit 0
else
    echo $password | sudo -S ifconfig ${var} ${password} down
    echo $password | sudo -S iwconfig ${var} mode monitor
    echo $password | sudo -S ifconfig ${var} up
    echo $password | sudo -S iwconfig ${var} channel 06
    echo "ifconfig ${var} is in success"
fi
# sudo ifconfig nic down
# sudo iwconfig nic mode monitor
# sudo ifconfig nic up
# sudo setcap cap_net_raw,cap_net_admin=eip client