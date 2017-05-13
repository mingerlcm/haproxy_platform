#!/usr/bin/env  python
# -*- coding:utf-8 -*-
#Author:minger
import os

def file_handle(file_name,backend_data,record_list = None,type ='search'):           #type search  append change
    new_file = file_name+"_new"
    bak_file = file_name+"_bak"
    cmd_copy = os.popen("copy %s %s.bak" % (file_name,file_name)).read()

    if type == 'search':
        r_list = []
        with open(file_name, "r", encoding="utf-8")as f:
            tag = False
            for line in f:  # line 每个人 逐行读取文件信息
                if line.strip() == backend_data:
                    tag = True
                    continue
                if tag and line.startswith("backend"):  # 如果以backend字符串开头
                    break
                if tag and line:
                    r_list.append(line.strip())
            for line in r_list:
                print(line)
            return r_list

    elif type =='append':
        with open(file_name,"r",encoding="utf-8")as read_file ,\
               open(new_file,'w',encoding="utf-8") as write_file:
            for read_line in read_file:     # 逐行读取
                write_file.write(read_line)     # 把旧文件写入到新文件

            for new_line in record_list:
                if new_line.startswith("backend"):
                    write_file.write(new_line+'\n')
                else:
                    write_file.write("%s%s\n" %(' '*8,new_line))
        print(cmd_copy)
        os.rename(file_name, bak_file)
        os.rename(new_file, file_name)
        os.remove(bak_file)





    elif type =='change':
        with open(file_name, "r", encoding="utf-8")as read_file, \
                open(new_file, 'w', encoding="utf-8") as write_file:
            tag = False # 警告
            has_write = False
            for read_line in read_file:  # 逐行读取文件中每行信息
                if read_line.strip() == backend_data:
                    tag = True  # 读到指定位置拉下警告
                    continue
                if tag and read_line.startswith('backend'):  # 如果警告响的又以backend字符串开头
                     tag = False
                if not tag:  # 如果警告没有响应
                    write_file.write(read_line)

                else:
                    if not has_write:  # 判断写了没有
                        for new_line in record_list:
                            if new_line.startswith("backend"):  # 如果以backend字符串开头
                                write_file.write(new_line + '\n')
                            else:
                                write_file.write("%s%s\n" % (' ' * 8, new_line))

                        has_write = True
        print(cmd_copy)
        os.rename(file_name,bak_file)
        os.rename(new_file, file_name)
        os.remove(bak_file)

def search(data):
    # backend www.oldboy.org
    backend_data ="backend %s" %data  # backend www.oldboy1.org
    return file_handle("haproxy.conf",backend_data,type ='search')

def add(data):
    backend= data['backend']
    record_list = search(backend)
    current_record ="server %s %s weight %s maxconn %s" %(data['record']['server'],\
                                                            data['record']['server'],\
                                                            data['record']['weight'],\
                                                            data['record']['maxconn'] )
    backend_data ="backend %s" %backend


    if not record_list:    # 添加的信息在原配置文件有没有的
        record_list.append(backend_data)
        record_list.append(current_record)  # 用户输入server记录
        return file_handle("haproxy.conf", backend_data,record_list,type='append')

    else:
        record_list.insert(0,backend_data)
        if  current_record not in record_list:   # 判断用户输入的server信息是否存在backend
            record_list.append(current_record)    # 把用户输入的server信息加入到backend下
        return file_handle("haproxy.conf", backend_data, record_list, type='change')

def remove(data):
    backend = data['backend']
    record_list = search(backend)
    current_record = "server %s %s weight %s maxconn %s" % (data['record']['server'], \
                                                            data['record']['server'], \
                                                            data['record']['weight'], \
                                                            data['record']['maxconn'])
    backend_data = "backend %s" % backend

    if not record_list or  current_record not in record_list:
        print("\033[33;1m 没有此记录\033[0m")
        return
    else:
        # 处理record_list
        record_list.insert(0,backend_data)  # 插入标题
        record_list.remove(current_record)  # 删除用户输入记录
        return file_handle("haproxy.conf", backend_data, record_list, type='change')

def change(data):
    backend = data[0]['backend']
    record_list = search(backend)
    old_record = "server %s %s weight %s maxconn %s" % (data[0]['record']['server'], \
                                                            data[0]['record']['server'], \
                                                            data[0]['record']['weight'], \
                                                            data[0]['record']['maxconn'])


    new_record = "server %s %s weight %s maxconn %s" % (data[1]['record']['server'], \
                                                        data[1]['record']['server'], \
                                                        data[1]['record']['weight'], \
                                                        data[1]['record']['maxconn'])
    backend_data = "backend %s" % backend

    if not record_list or old_record not in record_list:  # 添加的信息在原配置文件有没有的
        print("\033[32;1m 没有此记录\033[0m")
        return

    else:
        record_list.insert(0,backend_data)
        index = record_list.index(old_record)        # 获取老的记录的索引
        record_list[index] = new_record              # 用新的记录替换
        return file_handle("haproxy.conf", backend_data, record_list, type='change')


# 程序开始
if __name__ == '__main__':
    print("-------------------------------------------------")
    print("\t\t欢迎来到haproxy配置文件控制台")
    print("-------------------------------------------------")
    print("操作清单如下：")
    msg ='''
    1: 查询    
    2：添加
    3：删除
    4: 修改
    5：退出
        '''

    menu_dic ={
        '1':search,
        '2':add ,
        '3':remove,
        '4':change,
        '5':exit
    }
    while True:
        print(msg)
        user_choice =input("请输入操作的编号>>>:").strip()
        if user_choice not in msg:                 # 当输入不在编号中，提示并重新输入
            print("\033[31;1m输入错误请重新输入正确数字编号！\033[0m")

        if len(user_choice) == 0 or user_choice not in menu_dic :continue
        if user_choice == '5':break

        data = input("请输入数据内容>>>:").strip()

        # menu_dic[user_choice] == serch
        if user_choice != '1':
            data =eval(data)  #  字符串转换成字典格式

        menu_dic[user_choice](data)

