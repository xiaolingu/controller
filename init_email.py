#!/usr/bin/env python
# -*- coding: utf-8 -*-

## task: 
# 1.    link to the fixed AP "JESSC"
# 2.    start ssh service
# 3.    send me a email including the ip.

import sys, os, re, urllib, urlparse
import smtplib
import traceback
import netifaces
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


from iw_parser import find_netiface
'''
1.  link to the fixed AP 'JESSC'
    use supplicant_wpa to connect the wifi in target
    this operation will initialize in the open of computer.
'''


'''
2.  start the ssh
this part is setted in the raspberry pi. it isn't be considered

'''
'''
3.  send me a mail including the ip
function: sendmail
'''

def ip_msg(interface = 'wlan0'):
    try:
        addrs = netifaces.ifaddresses(interface)
        msg = addrs[2][0]['addr']
        if(msg == ""):
            raise Exception("msg is empty")
    except Exception as e:
        print e;
    return msg

'''find the netiface connected to JSSEC'''
    
def sendmail(subject, msg, toaddrs, fromaddr, smtpaddr, password):
    ''''' 
    @subject:邮件主题 
    @msg:邮件内容 
    @toaddrs:收信人的邮箱地址 
    @fromaddr:发信人的邮箱地址 
    @smtpaddr:smtp服务地址，可以在邮箱看，比如163邮箱为smtp.163.com 
    @password:发信人的邮箱密码 
    '''  
    mail_msg = MIMEMultipart()  
    if not isinstance(subject,unicode):  
        subject = unicode(subject, 'utf-8')  
    mail_msg['Subject'] = subject  
    mail_msg['From'] =fromaddr  
    mail_msg['To'] = ','.join(toaddrs)  
    mail_msg.attach(MIMEText(msg, 'html', 'utf-8'))  
    try:  
        s = smtplib.SMTP() 
        s.connect(smtpaddr) 
        s.login(fromaddr,password)  #登录邮箱  
        s.sendmail(fromaddr, toaddrs, mail_msg.as_string()) #发送邮件  
        print "successfully send email"
    except Exception,e:  
       print "Error: unable to send email"  
       print traceback.format_exc()     


if __name__ == '__main__':
    fromaddr = "lab_only@163.com"
    smtpaddr = "smtp.163.com"
    toaddrs = ["1030716893@qq.com"]
    subject = "test_email"
    password = "gu123456"

    res = find_netiface("JSSEC")
    if (res is not None):
        s = res[0]
    else:
        print "not find correct netiface"
        exit(0)
    msg = ip_msg(res[0])
    sendmail(subject, msg, toaddrs, fromaddr, smtpaddr, password)
    
    
