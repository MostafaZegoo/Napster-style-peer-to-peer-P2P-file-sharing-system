import sys
import socket
import pickle
from thread import *
#import functions

host = 'localhost'
port = 5325

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  #For only Unix and Linux

try:
    s.bind((host, port))
except socket.error, msg:
    print '# Failed with Error : ' + str(msg[0]) + ' Saying : ' + msg[1]
    sys.exit()
s.listen(10)

print 'Listening for connections'

onlinePeers = []
users = {}


def clientthread(conn, addr):
    conn.send(
        'Service Started. Choose an option Useing Uppercase letter\n #(R)egister\n #(U)pload files\n #(S)earch for a file\n #(E)xit')
    onlinePeers.append(addr[0])
    while True:
        data = conn.recv(1024)

        if not data:
            continue
        elif data.split('\n')[0] == 'REGISTER':

            nick = data.split('\n')[1]

            index = data.split('\n')[2]

            print index
            try:
                users = pickle.load(open("users", "rb"))
                # print users
            except:
                users = {}
                pickle.dump(users, open("users", "wb"))
            # print users[addr[0]]
            try:
                nickname = users[index]['nick']
                # print 'hi'
                conn.sendall('User already registered with nickname ' + nickname)
            except:
                users[str(index)] = {}
                users[str(index)]['nick'] = nick
                users[str(index)]['fileList'] = {}
                conn.sendall('You have been registered with nickname ' + nick)

            pickle.dump(users, open("users", "wb"))

        elif data.split('\n')[0] == 'SHARE_FILES':

            file = data.split('\n')[1]

            index = data.split('\n')[2]

            try:
                users = pickle.load(open("users", "rb"))
            except:
                conn.sendall('You need to register first')
                return
            try:
                nickname = users[str(index1)]['nick']
            except:
                conn.sendall('You need to register first')
                return

            fileName = file.split(' ')[0]
            # print fileName
            # filePath = file.split(' ')[1]
            # print filePath
            users[str(index1)]['fileList'][fileName] = fileName
            # print users
            pickle.dump(users, open("users", "wb"))
            conn.sendall('File ' + fileName + ' added')

        elif data.split('\n')[0] == 'SEARCH':

            fileName = data.split('\n')[1]

            activePeers = onlinePeers

            try:
                users = pickle.load(open("users", "rb"))
            # print users
            except:
                conn.sendall('ERROR\nNo users registered till now')
                return

            usersHavingFile = {}
            userList = users.keys()
            for user in userList:
                found = False
                # print users[user]['fileList'].keys()
                if fileName in users[user]['fileList'].keys():
                    # if user in activePeers:
                    usersHavingFile[user] = {}
                    usersHavingFile[user]['nick'] = users[user]['nick']
                    usersHavingFile[user]['filePath'] = users[user]['fileList'][fileName]
                    usersHavingFile[user]['port'] = users[user]

            conn.sendall(str(usersHavingFile))


    onlinePeers.remove(addr[0])
    conn.close()


while True:
    conn, addr = s.accept()
    print 'Got connection From ' + addr[0] + ':' + str(addr[1])
    start_new_thread(clientthread, (conn, addr))

s.close()
