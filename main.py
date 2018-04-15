#!/usr/bin/python
import os, sys, random, string, hashlib, subprocess, signal, socket, select, threading, time
from Tkinter import *

class MainWindow(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.title(string = " << Chat | Free Clear-text version >> ")

        self.options = {
            'host' : StringVar(),
            'port' : IntVar(),
            'username' : StringVar(),
            'key' : StringVar(),
            'chatbar' : StringVar(),
        }

        self.options['host'].set('127.0.0.1')
        self.options['port'].set(8989)

        settings = LabelFrame(self, text = 'Server', relief = GROOVE, labelanchor = 'nw', width = 570, height = 110)
        settings.grid(row = 0, column = 1)
        settings.grid_propagate(0)

        # Host entry
        Label(settings, text = 'Host:').grid(row = 0, column = 1)
        Entry(settings, textvariable = self.options['host']).grid(row = 0, column = 2, columnspan = 2)

        # Port entry
        Label(settings, text = 'Port:').grid(row = 1, column = 1)
        Entry(settings, textvariable = self.options['port']).grid(row = 1, column = 2, columnspan = 2)

        # Username entry
        Label(settings, text = 'Username:').grid(row = 2, column = 1)
        username_entry = Entry(settings, textvariable = self.options['username']).grid(row = 2, column = 2, columnspan = 2)

        # Key entry
        Label(settings, text = 'Key:').grid(row = 3, column = 1)
        key_entry = Entry(settings, textvariable = self.options['key'], show = '*').grid(row = 3, column = 2, columnspan = 2,)

        # Chat Frame
        chat = LabelFrame(self, text = 'Chat', relief = GROOVE)
        chat.grid(row = 3, column = 1, rowspan = 4)
        self.options['chatbox'] = Text(chat, foreground="black", background="white", highlightcolor="white", highlightbackground="black", wrap=NONE, height = 28, width = 80)
        self.options['chatbox'].grid(row = 0, column = 1)
        self.options['chatbox'].insert(END, 'Set Host and port, then click Connect to enter a server.\nOr click Host to host a chat server on the given port\n')

        # Connect button
        connect_button = Button(self, text = "Connect!", command = self.connect, width = 70).grid(row = 1, column = 0, columnspan = 2)

        # Host button
        host_server_button = Button(self, text = "Host", command = self.host, width = 70).grid(row = 2, column = 0, columnspan = 2)

        # Send text entry
        self.options['chatbar'] = Entry(chat, textvariable = self.options['chatbar'], width = 70)
        self.options['chatbar'].grid(row = 1, column = 0, columnspan = 4)
        submit = Button(self, text = "Submit", command = self.send_message, width = 70).grid(row = 7, column = 0, columnspan = 2)
        self.options['chatbar'].bind('<Return>', self.send_message) # Send message with the Return key (aka Enter)
        self.options['chatbar'].focus()

    # Socket connection
    global s
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)

    def connect(self):
        self.options['chatbox'].insert(END, 'Connecting as %s to %s:%s....\n' % (self.options['username'].get(), self.options['host'].get(), self.options['port'].get()))
        thread = threading.Thread(target=self.keep_alive)
        thread.daemon = True
        thread.start()

    def exit(self):
        sys.exit(0)

    def keep_alive(self):

        try:
            s.connect((self.options['host'].get(), int(self.options['port'].get())))
            self.options['chatbox'].insert(END, 'Connected, Welcome!\n')
            connect_button = Button(self, text = "Quit", command = self.exit, width = 70).grid(row = 1, column = 0, columnspan = 2)
        except Exception as e:
            self.options['chatbox'].insert(END, 'Failed to connect: %s\n' % e)

        running = True

        while running:
            socket_list = [sys.stdin, s]

            # Get the list sockets which are readable
            read_sockets, write_sockets, error_sockets = select.select(socket_list , [], [])

            for sock in read_sockets:
                if sock == s:
                    data = sock.recv(1024)
                    if not data:
                        self.options['chatbox'].insert(END, 'Disconnected from server\n')
                        sys.exit(1)
                    else:
                        # Show data
                        self.options['chatbox'].insert(END, '%s\n' % data.strip())

    def send_message(self, event):
        # Send message
        message = '[%s] %s ' % (self.options['username'].get(), self.options['chatbar'].get())
        self.options['chatbox'].insert(END, '%s \n' % message)
        s.send(message) # Send message
        self.options['chatbar'].delete(0, END) # Clear chatbar

    def host(self):
        key = hashlib.sha256(gen_string()).hexdigest()
        self.options['chatbox'].insert(END, '\nYour key: %s\n' % key)
        self.options['chatbox'].insert(END, 'Others need this key to connect with your server to secure the connection\n')

        # Open server
        server = subprocess.Popen(['python ./server.py %s %i %s' % (self.options['host'].get(), int(self.options['port'].get()), key)], stdout=subprocess.PIPE, shell=True)

        # Change to stop server button
        host_server_button = Button(self, text = "Stop server", command = self.stop_server, width = 70).grid(row = 2, column = 0, columnspan = 2)


    def stop_server(self):
        try:
            proc = subprocess.Popen("netstat -tulpn | grep %s" % self.options['port'].get(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            pid, err = proc.communicate()

            pid = pid.split('/')
            pid[0] = pid[0].split(' ')
            print(pid[0][-1])

            # Kill PID
            os.kill(int(pid[0][-1]), signal.SIGKILL)

            # Change button to host
            host_server_button = Button(self, text = "Host", command = self.host, width = 70).grid(row = 2, column = 0, columnspan = 2)

        except Exception as e:
            print(e)
            pass

        self.options['chatbox'].insert(END, 'Server closed... Killed PID %i\n' % int(pid[0][-1]))

# Generate a key for server hosting
def gen_string(size=32, chars=string.ascii_uppercase + string.digits):
      return ''.join(random.choice(chars) for _ in range(size))

if __name__ == '__main__':
    try:
        main = MainWindow()
        main.mainloop()
    except Exception as e:
        print('There was an error: %s\n' % e)
