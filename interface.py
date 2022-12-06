import socket, json

interface_port = 7999

local_ip = '127.0.0.1'

udp = None

def create_interface_socket():
  global udp
  udp = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
  udp.bind((local_ip, int(interface_port)))

def send_msg(num, msg, ip, port):
  global udp

  msg = { 'command_number': num, 'message': msg }

  msg = json.dumps(msg)

  msg = msg.encode('utf-8')

  udp.sendto(msg, (ip, int(port)))

def read_commands():
  while True:
    global udp
    try:
      in_ = input()
      ip1, porto1, x = in_.split(' ')[:3]

      if ip1 == 'x':
        ip1 = local_ip
      
      if x == 'C':
        ip2, porto2, nome = in_.split(' ')[3:]
        if ip2 == 'x':
          ip2 = local_ip

        send_msg(77777, f'C {ip2} {porto2} {nome}', ip1, porto1)

      elif x == 'D':
        name = in_.split(' ')[3:]
        name = name[0]

        send_msg(22222, f'D {name}', ip1, porto1)

      elif x == 'I':
        send_msg(33333, 'I', ip1, porto1)

      elif x == 'F':
        send_msg(44444, 'F', ip1, porto1)

      elif x == 'T':
        send_msg(55555, 'T', ip1, porto1)

      elif x == 'E':
        txt, dest = in_.split(' ')[3:]
        send_msg(66666, f'E {txt} {dest}', ip1, porto1)

    except ValueError:
      print('comando inválido')
      continue

create_interface_socket()
read_commands()