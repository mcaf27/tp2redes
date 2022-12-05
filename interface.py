from router import Router
import socket

interface_port = 7999

local_ip = '127.0.0.1'

conn = None

def create_interface_connection():
  global conn
  conn = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
  conn.bind((local_ip, int(interface_port)))

def send_msg(msg, ip, port):
  global conn

  msg = msg.encode('utf-8')
  conn.sendto(msg, (ip, int(port)))

def read_commands():
  while True:
    global conn
    try:
      in_ = input()
      ip1, porto1, x = in_.split(' ')[:3]

      if ip1 == 'x':
        ip1 = local_ip
      
      if x == 'C':
        ip2, porto2, nome = in_.split(' ')[3:]
        if ip2 == 'x':
          ip2 = local_ip

        send_msg(f'C {ip2} {porto2} {nome}', ip1, porto1)

      elif x == 'D':
        ip2, porto2 = in_.split(' ')[3:]
        # tá correto assim no enunciado mesmo?

      elif x == 'I':
        send_msg('I', ip1, porto1)

      elif x == 'F':
        send_msg('F', ip1, porto1)

      elif x == 'T':
        send_msg('T', ip1, porto1)

      elif x == 'E':
        txt, dest = in_.split(' ')[3:]
        send_msg(f'E {txt} {dest}', ip1, porto1)

    except ValueError:
      print('comando inválido')
      continue

create_interface_connection()
read_commands()