import sys
from subprocess import Popen
import os
import hashlib
import struct
import getopt
import socket
import re
import string
import time

FLAG = {1: "NO_ERROR", 2: "ERROR_RESET", 0: "RESTART"}
data_par_path = os.getcwd()
data_save_path = os.path.join(data_par_path, 'data')
msg_hello = 'hi, I am center controller'
msg_bye = 'bye, I am center controller'
reply_hello = 'monitor has already opened!'
reply_bye = 'monitor has already closed!'
HEAD_STRUCT = '128sIq32s'
BUFFER_SIZE = 1024


class dealer(object):
    def __init__(self, local_ip='127.0.0.1', local_port=9999):
        self.local_ip = local_ip
        self.local_port = local_port
        self.addr = (local_ip, local_port)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    @staticmethod
    def address_valid(local_ip, local_port):
        p = re.compile('^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
        if p.match(local_ip):
            pass
        else:
            raise ValueError("ip format is correct!!!")
        if (isinstance(local_port, int) == False):
            raise TypeError("local_port format should be int type!!!")
        elif (local_port > 65535 or local_port < 1025):
            raise ValueError("local port should be in 1025 - 65535")
        return True

    def set_element(self, local_ip, local_port):
        self.address_valid(local_ip, local_port)
        self.addr = (local_ip, local_port)

    def mons_accept(self):
        return self.s.accept()

    def start_server(self):
        self.s.bind(self.addr)
        self.s.listen(2)

    
def cal_md5(file_path):
    with open(file_path, 'rb') as fr:
        md5 = hashlib.md5()
        md5.update(fr.read())
        md5 = md5.hexdigest()
        return md5


def get_file_info(file_path):
    file_name = os.path.basename(file_path)
    file_name_len = len(file_name)
    file_size = os.path.getsize(file_path)
    md5 = cal_md5(file_path)
    return file_name, file_name_len, file_size, md5


def send_file(file_path, conn):
    file_name, file_name_len, file_size, md5 = get_file_info(file_path)
    file_head = struct.pack(HEAD_STRUCT, file_name, file_name_len, file_size, md5)
    try:
        print "send file!!!"
        conn.send(file_head)
        rest_size = file_size
        with open(file_path, 'rb') as fr:
            while 1:
                file_data = fr.read(BUFFER_SIZE)
                if not file_data:
                    break
                conn.send(file_data)
            fr.close()
        print "[line:%s] file has been sent!!!" % (sys._getframe().f_lineno)
    except socket.error, e:
        print "Socket ERROR: %s" % str(e)


def catch_work(save_path, conn):
    file_path = os.listdir(save_path)
    if (len(file_path) == 0):
        pass
    else:
        for i in file_path:
            os.remove(os.path.join(save_path, i))
    pid = Popen(['./client', '-d', 'wlan1', '-c', '06'])
    time.sleep(300)
    print pid.kill()
    file_path = os.listdir(save_path)
    if (len(file_path) == 0):
        print "client doesn't catch any packet!!"
        return 1
    else:
        send_file(os.path.join(save_path, file_path[0]), conn)
        ##time.sleep(1)
        return 1


def mons_mission(data, conn):
    if (data == "1"):
        if (catch_work(data_save_path, conn) == 1):
            return 1
        else:
            return 2
    elif (data == msg_hello):
        conn.send(reply_hello)
        return 1
    elif (data == msg_bye):
        conn.send(reply_bye)
        conn.close()
        return 0
    else:
        raise Exception("don't receive the valid intro!!!")


def schedule_work(ip, port):
    flag = 1
    ## todo: dealer and mons_mission
    a = dealer()
    a.set_element(ip, port)
    ## when start ?
    a.start_server()
    con, addr = a.mons_accept()
    while (1):
        try:
            if (flag == 1):
                data = con.recv(1024)
                flag = mons_mission(data, con)
            elif (flag == 0):
                print "mons finish the mission!!!"
                flag = 1
                con.close()
                con, addr = a.mons_accept()
            elif (flag == 2):
                print "files cann't be opened in success"
                con.close()
                raise Exception("file op is error")
        except Exception as e:
            print e
            print "all mons must be closed, need to check"
            con.close()
            break


if __name__ == '__main__':
    ip = "127.0.0.1"
    port = 9999
    try:
        opts, args = getopt.getopt(sys.argv[1:], "i:p:", ["ip", "port"])
        for name, value in opts:
            if name in ("-i", "--ip"):
                ip = value
            elif name in ("-p", "--port"):
                port = string.atoi(value)
        schedule_work(ip, port)
    except getopt.GetoptError:
        sys.exit()
