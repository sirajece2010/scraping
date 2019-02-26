import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime, date
import time, re
import csv
import smtplib
import config

first_flag = True
lst_list_str = []
head_list = ['Date','24k_1gram','24k_8gram','22k_1gram','22k_8gram','Date_Captured','Time_captured']
script_date = str(datetime.date(datetime.now()))
output_file_name = 'result.csv'

try:
    with open('result.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
        for val in csv_reader:
            lst_list_str = '|'.join(val)[:50]
    with open('result.csv') as fh:
        file_content = fh.readlines()
    #print(lst_list_str)

except IOError:
    with open('result.csv', 'a+') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(head_list)
    with open('result.csv') as fh:
        file_content = fh.readlines()

def get_content(url,method,data=None):
   call_function = getattr(requests, method)
   if method == 'get':
       return call_function(url).text
   if method == 'post' or method == 'put' or method == 'del':
       return call_function(url,data).text

def read_content(file_name):
    with open ('{}'.format(file_name)) as fh:
        ret_content = fh.readline()
    return  ret_content



def send_mail(subject, content):
    mail = smtplib.SMTP('smtp.gmail.com', 587)
    mail.ehlo()
    mail.starttls()
    mail.ehlo()
    mail.login(config.from_mail, config.mail_passwd)
    headers = [
        "From: " + config.from_mail,
        "Subject: " + subject,
        "To: " + config.to_mail,
        "MIME-Version: 1.0",
        "Content-Type: text/html"]
    headers = "\r\n".join(headers)
    mail.sendmail(config.from_mail, config.to_mail, headers + "\r\n\r\n" + content)
    mail.close()

while True:
    today = str(date.today())
    #today = '2019-02-12'
    if first_flag:
        print('first if')
        first_flag = False
        content = get_content('http://www.livechennai.com/gold_silverrate.asp','get')
        #content = read_content('output_2019-02-12.html')
        fh = open('output_{}.html'.format(today), 'w')
        #fh.write(content.encode('utf-8'))
        fh.write(content)
        fh.close()

        soup = BeautifulSoup(content, 'html.parser')

        a = soup.find('table')
        b = soup.find_all('table', class_='table-price')

        for i in range(49, 0, -5):
            date_ = str(b[1].find_all('td', class_='content')[i - 4].text).strip()
            k24rate1 = str(b[1].find_all('td', class_='content')[i - 3].text).strip()
            k24rate8 = str(b[1].find_all('td', class_='content')[i - 2].text).strip()
            k22rate1 = str(b[1].find_all('td', class_='content')[i - 1].text).strip()
            k22rate8 = str(b[1].find_all('td', class_='content')[i].text).strip()
            current_time = str(datetime.time(datetime.now()))
            my_list = [date_, k24rate1, k24rate8, k22rate1, k22rate8]
            cur_list_str = ','.join(my_list)
            print(my_list)
            if any(date_ in val for val in file_content):
                pass
            else:
                my_list.extend([today, current_time])
                with open('result.csv', 'a+') as csv_file:
                    writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    writer.writerow(my_list)

    elif (script_date not in today) or (re.match(r'^15\:[1-4]\d\:',current_time)):
        print('first elif')

        content = get_content('http://www.livechennai.com/gold_silverrate.asp', 'get')
        # content = read_content('output_2019-02-12.html')
        soup = BeautifulSoup(content, 'html.parser')

        a = soup.find('table')
        b = soup.find_all('table', class_='table-price')

        date_ = str(b[1].find_all('font')[0].text).strip()
        k24rate1 = str(b[1].find_all('font')[1].text).strip()
        k24rate8 = str(b[1].find_all('font')[2].text).strip()
        k22rate1 = str(b[1].find_all('font')[3].text).strip()
        k22rate8 = str(b[1].find_all('font')[4].text).strip()

        current_time = str(datetime.time(datetime.now()))
        my_list = [date_, k24rate1, k24rate8, k22rate1, k22rate8]
        cur_list_str = '|'.join(my_list)
        my_list.extend([today, current_time])

        if (re.match(r'^[1][0]\:[0-4]\d\:',current_time)) and (cur_list_str != lst_list_str):
            print('Today\'s_Gold_Rate: time {}'.format(current_time))
            print(my_list)
            with open('result.csv', 'a+') as csv_file:
                writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                writer.writerow(my_list)
            body = date_ + '=>' + k22rate1 + ' ' + k22rate8
            send_mail("Today's_Gold_Rate", body)
            lst_list_str = cur_list_str
            
        elif cur_list_str != lst_list_str:
            print('Gold_Rate_Change_Notification:{} {}'.format(cur_list_str,lst_list_str))
            print(my_list)
            with open('result.csv', 'a+') as csv_file:
                writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                writer.writerow(my_list)
            body = date_ + '=>' + k22rate1 + ' ' + k22rate8
            send_mail("Gold_Rate_Change_Notification", body)
            lst_list_str = cur_list_str
        time.sleep(2*60)
        fh = open('output_{}.html'.format(today), 'w')
        fh.write(str(a))
        fh.close()
    else:
        current_time = str(datetime.time(datetime.now()))
        print ('Script started on {} and today is {} time::{}'.format(script_date, today, current_time))
        time.sleep(6 * 60)
