import sys
import socket
import threading
import time
import struct 
import hashlib
import os
import traceback
import gc

mon_list = ['0','1','2']
# '0': "192.168.96.253", '1': "192.168.97.177", '2': "192.168.96.242"
ip_set = {'0': "192.168.96.253",'1': "192.168.97.177", '2': "192.168.96.242"}
mon_len = len(ip_set)
## two-tuples
socket_dict = {}
port = 9999
bufflen = 1024
timeout = 5
msg_hello = 'hi, I am center controller'
msg_bye = 'bye, I am center controller'
intro_abbr = {"catch" : "1", "send": "2"}
## frame info structure
HEAD_STRUCT = '128sIq32s'
info_size = struct.calcsize(HEAD_STRUCT)
DATA_FILE_PATH = os.getcwd() + '/new_data'
recv_thread_info = {}

class thread_recv_info(object):
    def _init_(self):
        self.file_path = ''
    def setfile_path(self, file_path):
        self.file_path = file_path

def cal_md5(file_path):
    with open(file_path, 'rb') as fr:
        md5 = hashlib.md5()
        md5.update(fr.read())
        md5 = md5.hexdigest()
        return md5

def unpack_file_info(file_info):
    file_name, file_name_len, file_size, md5 = struct.unpack(HEAD_STRUCT, file_info)
    file_name = file_name[:file_name_len]
    return file_name, file_size, md5

def recv_file(st):
    try:
        file_info_package = st.recv(info_size)
        file_name, file_size, md5_recv = unpack_file_info(file_info_package)

        rest_size = file_size
        file_path = os.path.join(os.getcwd() + '/new_data', file_name)
        print file_path

        recv_thread = thread_recv_info();
        recv_thread.file_path = file_path

        with open(os.path.join(os.getcwd() + '/new_data', file_name), 'wb') as fw:
            while 1:
                if rest_size > bufflen:
                    file_data = st.recv(bufflen)
                else:
                    file_data = st.recv(bufflen)
                if not file_data: break
                fw.write(file_data)
                rest_size = rest_size - len(file_data)
                if rest_size == 0:
                    break
        fw.close()
        md5 = cal_md5(file_path)
        if md5 != md5_recv:
            print 'MD5 compared fail!'
        else:
            print 'MD5 compared successfully!!!'
            print 'file Received successfully!!!'
    except socket.errno, e:
        print "Socket error: %s" % str(e)
    return recv_thread

def open_socket(addr_dict):
    st = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        socket_dict[addr_dict] = st
    except Exception as e:
        print e
        sys.exit()
    st.connect(addr_dict)
    return st

def close_socket(st):
    st.close()

def order_start(addr_dict):
    st = open_socket(addr_dict)
    st.send(msg_hello)
    while(True):
        begin = time.time()
        try:
            data = st.recv(bufflen)
            if data == 'monitor has already opened!':
                print "monitor open successfully!!!"
                break
        except Exception as e:
            print 'order_start_fail!'
            close_socket(st)
            sys.exit(0)
    return st

def order_end(st):
    st.send(msg_bye)
    while(True):
        try:
            data = st.recv(1024)
            if(data == 'monitor has already closed!'):
                print "monitor pause successfully!!!"
                break
        except Exception as e:
            print 'order_end_fail!'
            close_socket(st)
            sys.exit(0)
    close_socket(st)

def order_send_data(st):
    st.send(intro_abbr["catch"])
    
def order(choice, i, addr_dict):
    if choice == '0':
        st = order_start(addr_dict)
        ## todo: some operations
        order_end(st)
    elif choice == '1':
        st = order_start(addr_dict)
        order_send_data(st)
        ## count the number of files by receiving from mon
        if i in recv_thread_info:
            print 'recv_thread_info had not been cleared in last time'
            sys.exit(0)
        else:
            recv_thread_info[i] = recv_file(st)
        order_end(st)
    else:
        sys.exit(0)

def mon_ops(choice, ip_set):
    global socket_dict
    addr_dict = {}
    for i in ip_set.keys():
        print "i:", i
        addr_dict[i] = (ip_set[i], port)
    try:
        if choice == '1':
            threads_mon = {}
            for i in ip_set.keys():
                threads_mon[i] = threading.Thread(target=order, args=(choice, i, addr_dict[i]))
                threads_mon[i].start()
            for i in ip_set.keys():
                threads_mon[i].join()
        if(len(recv_thread_info)!= mon_len):
            raise Exception("operation is error")
    except Exception as e:
        print e
        print 'mon_ops is in failure'
        for i in socket_dict.keys():
            close_socket(socket_dict[i])
            del socket_dict[i]
        sys.exit()
    
    finally:
        for i in socket_dict.keys():
            close_socket(socket_dict[i])
        del socket_dict
        socket_dict = {}

def merge_file(recv_thread_info, i):
    '''
    @function:
        merge the file to target file 'i' and remove the original file
    
    @Arg:   i : index of cnt

    @return:
    '''
    new_file_name = DATA_FILE_PATH + '/' + str(i) + '.txt'
    obj = open(new_file_name, 'wb+')
    for K in mon_list:
        try:
            if recv_thread_info.has_key(K) is False:
                raise Exception('mon is error')
        except Exception as e:
            traceback.print_exc()
            sys.exit(0)
        mon_file_path = recv_thread_info[K].file_path
        fd_mon = open(mon_file_path, 'r');
        obj.writelines(fd_mon.readlines())
        os.remove(mon_file_path)
        fd_mon.close()
    obj.close()

def schedule(ip_set, choice = '1', cnt = 100):
    global recv_thread_info
    for i in xrange(cnt):
        print "cnt: %d" % (i)
        mon_ops(choice, ip_set)
        merge_file(recv_thread_info, i)
        recv_thread_info = {}

if __name__ == '__main__':
    # for i in mon_list:
    #     recv_thread_info[i] = thread_recv_info()
    #     recv_thread_info[i].setfile_path(DATA_FILE_PATH + '/test_' + i + '.txt')
    #     ## print 'mon' + i + ' ' + recv_thread_info[i].file_path
    
    # merge_file(recv_thread_info, 1)
    schedule(ip_set, '1', 100)

    
