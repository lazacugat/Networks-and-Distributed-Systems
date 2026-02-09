# encoding: utf-8
# Revisión 2019 (a Python 3 y base64): Pablo Ventura
# Copyright 2014 Carlos Bederián
# $Id: connection.py 455 2011-05-01 00:32:09Z carlos $

import socket
from constants import *
from base64 import b64encode
import os

def error_msg(code):
    code_msg = str(code)
    error_msg = str(error_messages[code])
    return (code_msg  + " " + error_msg + EOL)

class Connection(object):
    """
    Conexión punto a punto entre el servidor y un cliente.
    Se encarga de satisfacer los pedidos del cliente hasta
    que termina la conexión.
    """

    def __init__(self, socket, directory):
        self.connection_socket = socket
        self.directory = directory
        self.connected = True
        self.buffer = ""            

    def is_valid_input(self, input):
        for i in input:
            # Ignorar espacios
            if i == " ":
                continue
            # Verificar si el caracter esta en la lista de caracteres validos
            if i not in VALID_CHARS:
                return False
        return True

    def send_b64_response(self,code,response):
        code_msg = error_msg(code)
        code_msg = code_msg.encode("ascii")
        response = b64encode(response)
        eol = EOL.encode("ascii")
        try:
            self.connection_socket.send(code_msg)
            self.connection_socket.send(response)
            self.connection_socket.send(eol)
        except Exception as e:
            print(f"exception sending response: {e}")

    def send_ascii_response(self,code,response): 
        send_msg = error_msg(code)
        if not response:
            send_msg = send_msg.encode('ascii')
        else : 
            send_msg += response + EOL
            send_msg = send_msg.encode('ascii')
        try:
            self.connection_socket.send(send_msg)
        except Exception as e:
            print(f"exception sending response: {e}")
        
    def read_line(self):
        while not EOL in self.buffer and self.connected:
            try:
                self.buffer += self.connection_socket.recv(BUFFER).decode("ascii")
            except UnicodeError:
                self.send_ascii_response(BAD_REQUEST,"")
                self.connected = False
                print("Closing connection...")
        if EOL in self.buffer :
            line, self.buffer = self.buffer.split(EOL, 1)
            return line.strip()
        else:
            return ""

    def execute_line(self,line) :
        args = line.split(" ")
        if args[0] not in client_commands:
            self.send_ascii_response(INVALID_COMMAND,"")
        elif not self.is_valid_input(line):
            self.send_ascii_response(INVALID_ARGUMENTS,"")
        elif args[0] == client_commands[0] and len(args) == 1 :
            self.quit()
        elif args[0] == client_commands[1] and len(args) == 1:
            self.get_file_listing()
        elif args[0] == client_commands[2] and len(args) == 2:
            self.get_metadata(args[1])
        elif args[0] == client_commands[3] and len(args) == 4 and args[2].isdecimal() and args[3].isdecimal():
            self.get_slice(args[1],int(args[2]),int(args[3]))
        else :
            self.send_ascii_response(INVALID_ARGUMENTS,"")
 
    def get_slice(self, filename, offset, size):
        #verificamos que el archivo exista
        if not os.path.exists(os.path.join(self.directory, filename)):
            self.send_ascii_response(FILE_NOT_FOUND,"")

        else:
            length = os.path.getsize(os.path.join(self.directory, filename))
            #chequeamos los argumentos
            if offset > length or offset < 0 or size > length:
                self.send_ascii_response(BAD_OFFSET,"")
            #abrimos el archivo y buscamos el slice
            else :
                with open(os.path.join(self.directory, filename), "rb") as file:
                    file.seek(offset)
                    slice = file.read(size)

                    #lo decodeamos de ascii y encodeamos a base64
                    self.send_b64_response(CODE_OK, slice)

    def get_metadata(self,filename) :
        if not os.path.exists(os.path.join(self.directory,filename)):
            self.send_ascii_response(FILE_NOT_FOUND,"")
        else :
            response = os.path.getsize(os.path.join(self.directory,filename))
            response = str(response)
            self.send_ascii_response(CODE_OK,response)

    def get_file_listing(self):
        response = ""
        for file in os.listdir(self.directory) :
            response += file + EOL
        self.send_ascii_response(CODE_OK,response)

    def quit(self) : 
        try:
            print("Closing connection...")            
            self.send_ascii_response(CODE_OK,"")
            self.connected= False
        except socket.error as e:
            print(f"error cerrando socket: {e}")

    def handle(self):
        while self.connected :
            line = self.read_line()
            if NEWLINE in line:
                self.send_ascii_response(BAD_EOL,"")
                self.connected = False
                print("Closing connection...")
            else :
                try : 
                    self.execute_line(line)
                except Exception:
                    self.send_ascii_response(INTERNAL_ERROR,"")
                    self.connected = False
                    print("Closing connection...")
        self.connection_socket.close()