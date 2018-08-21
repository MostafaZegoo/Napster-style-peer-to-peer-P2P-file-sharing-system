import socket
# from thread import *
import sys
import threading
from thread import start_new_thread
from threading import Thread
import pickle
import os.path

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error, msg:
    print 'Socket is not created. Due to error : ' + str(msg[0]) + ' ,Saying : ' + msg[1]
    sys.exit()

ClientListener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#ClientListener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) used in Unix and Linux


portL = pickle.load(open(os.path.dirname(__file__) + '/../port', "rb"))
pickle.dump(portL + 1, open(os.path.dirname(__file__) + '/../port', "wb"))

try:
    ClientListener.bind(('', portL))
except socket.error, msg:
    print 'Bind failed. Error Code: ' + str(msg[0]) + ' Message: ' + msg[1]
    sys.exit()
ClientListener.listen(10)
print "Socket now listening"


def client(host, port, s, portL):
    try:
        remote_ip = socket.gethostbyname(host)
    except socket.gaierror:
        print 'Hostname couldn\'t be resolved. Exiting'
        sys.exit()

    s.connect((remote_ip, port))

    print 'Socket connected to ' + host + ' on ip ' + remote_ip

    reply = s.recv(4096)

    print reply

    while True:
        input = raw_input(">> ")
        if not input:
            continue
        elif input[0] is 'U':
            fileName = raw_input('Enter file name: ')
            if not fileName:
                print 'Not valid input'
                continue
            # filePath = raw_input('Enter path: ')
            # if not filePath:
            #     print 'Not valid input'
            #     continue
            message = 'SHARE_FILES\n' + fileName + "\n" +str(portL)

        elif input[0] is 'R':
            nickname = raw_input('Enter a nickname: ')

            if not nickname:
                print 'Not valid input'
                continue
            print str(portL) + "Port"
            message = 'REGISTER\n' + nickname +"\n"+ str(portL)

        elif input[0] is 'S':
            fileName = raw_input('Enter file name to be searched: ')
            if not fileName:
                print 'Not valid input'
                continue
            message = 'SEARCH\n' + fileName
            try:
                s.sendall(message)
            except socket.error:
                print 'Send failed'
                sys.exit()
            reply = s.recv(4096)
            if reply == "{}":
                print 'No such a File'
                continue
            elif reply.split('\n')[0] == 'ERROR':
                print reply.split('\n')[1]
                sys.exit()

            usersHavingFile = eval(reply)  # convert reply into dictionary
            print usersHavingFile
            if not usersHavingFile:
                reply.sendall('File not found')
                continue

            message = 'The following users have the file:\n'
            for user in usersHavingFile.keys():
                message = message + usersHavingFile[user]['nick'] + ' (' + user + ') (' + usersHavingFile[user][
                    'filePath'] + ')\n'
            print message
            response = raw_input(
                'Write \"Q\" Then a space followed by the client IP to download the file from the client')
            if not response:
                print 'Not valid input pickup a chooise again'
                continue
            response = response.strip()

            if response[0] == 'Q':
                s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                peerIP = response.split(' ')[1]
                print peerIP
                s1.connect(('127.0.0.1', int(peerIP)))
                queryMessage = 'DOWNLOAD\n' + fileName + '\n' + usersHavingFile[peerIP]['filePath']
                try:
                    s1.sendall(queryMessage)
                except socket.error:
                    print 'Send failed'
                    sys.exit()
                fw = open(fileName , 'wb+')
                flag = 0
                chunk = s1.recv(20480)
                while chunk != 'SHUT_WR':
                    s1.send('received')
                    if chunk.split('\n')[0] == 'ERROR':
                        print chunk.split('\n')[0] + ' ' + chunk.split('\n')[1]
                        flag = 1
                        break
                    fw.write(chunk)
                    chunk = s1.recv(100)
                if flag != 1:
                    print "\nFile saved in the receivedFiles folder inside your current folder"

                else:
                    print "\nError while downloading the file"
                fw.close()
                s1.close()

            continue
        elif input[0] is 'E':
            s.close()
            ClientListener.close()
            sys.exit()
            break
        else:
            print 'Unknown command'
            continue

        try:
            s.sendall(message)
        except socket.error:
            print 'Send failed'
            sys.exit()

        reply = s.recv(4096)

        print reply

    s.close()


###########################################


def listenForSharing(ClientListener):
    while True:
        conn, addr = ClientListener.accept()
        data = conn.recv(1024)

        if data.split('\n')[0] == 'DOWNLOAD':
            fileName = data.split('\n')[1]
            try:
                dir_path = os.path.dirname(os.path.abspath(__file__))
            except NameError:  # We are the main py2exe script, not a module
                import sys
                dir_path = os.path.dirname(os.path.abspath(sys.argv[0]))
            print dir_path+"\\"+fileName
            try:
                fr = open(dir_path+"\\"+fileName, 'rb')
            except:
                conn.sendall('ERROR\nNo such file available')
                continue
            chunk = fr.read()
            conn.send(chunk)
            ack = conn.recv(100)

        conn.sendall('SHUT_WR')
    ClientListener.close()


###########################################


try:

    host = 'localhost'
    port = 5325

    if __name__ == '__main__':
        Thread(target=client, args=(host, port, s, portL)).start()
        Thread(target=listenForSharing, args=(ClientListener,)).start()
except:
    ClientListener.close()
