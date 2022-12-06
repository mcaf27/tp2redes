import socket
import json
import threading
import time
from sys import argv

local_ip = '127.0.0.1'
buffer_size = 1024

class RouterTable:
  def __init__(self, dest, dist, next):
    self.table = [{ 'dest': dest, 'dist': dist, 'next': next }]

  def __repr__(self):
    return f'{self.table}'
  
  def add_entry(self, dest, dist, next):
    self.table += [{ 'dest': dest, 'dist': dist, 'next': next }]

  def remove_entry(self, nome):
    new_table = []
    for entry in self.table:
      if entry['dest'] == nome or entry['next'] == nome:
        entry['dist'] = 16 #infinito
      new_table.append(entry)

  def get_next_hop(self, dest):
    for item in self.table:
      if item['dest'] == dest:
          return item['next']

class Router:
  def __init__(self, id, port, ip=local_ip):
    self.id = id
    self.ip_addr = ip
    self.port = port
    self.table = RouterTable(id, 0, id)
    self.udp = None
    self.links = []
    self.timer = None
    self.stop = False

  def __eq__(self, obj):
    if isinstance(obj, Router):
      return self.id == obj.id
    return  self.id == obj

  def __repr__(self):
    return f'{self.id}:{self.ip_addr}/{self.port}'

  def continue_(self):
    return not self.stop

  def timer_f(self):

    def f():
      if self.continue_():
        self.init_roteamento()
        self.timer_f()
    
    thread = threading.Timer(1, f)
    thread.start()
    return thread

  def get_router_index_from_table(self, router_name):
    for index, item in enumerate(self.table.table):
        if item['dest'] == router_name:
            return index
    return -1

  def update_table(self, new_table, name_sender):
    for item in new_table:
        dest, dist = item.values()
        index = self.get_router_index_from_table(dest)
        route_in_table = self.table.table[index]
        next = route_in_table.get('next')
        
        if index == -1:
            self.table.table.append({ 'dest': dest, 'dist': dist + 1, 'next': next })
        else:
            if dist + 1 < route_in_table['dist']:
                self.table.table[index] = { 'dest': dest, 'dist': dist + 1, 'next': next }
            else:
                if route_in_table['next'] == name_sender:
                    self.table.table[index] = { 'dest': dest, 'dist': dist + 1, 'next': next }

  def bind(self):
    self.udp = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    # print(self.ip_addr, self.port, self.id)
    self.udp.bind((self.ip_addr, int(self.port)))

  def recv(self):
    msg_, addr = self.udp.recvfrom(buffer_size)
    
    msg = msg_.decode('utf-8')

    msg = json.loads(msg)

    command_number = msg.get('command_number')
    name_sender = msg.get('name_sender')
    routes = msg.get('routes')
    message = msg.get('message')

    if command_number == 11111:
      self.update_table(routes, name_sender)
    
    elif command_number == 99999:

      destination = msg.get('name_destination')
      text = msg.get('text')

      if destination == self.id:
        print(f'R {text} de {name_sender} para {destination}')
        print()
        # descartada
      else: # destino != self
        next_router_name = self.table.get_next_hop(destination)
        link_to_forward = None

        for link in self.links:
          if link.id == next_router_name:
            link_to_forward = link
            break

        if link_to_forward is None:
          print(f'X {text} de {name_sender} para {destination}')
          print()
          # descartada
        else: # destino está na tabela de vizinhos
          self.send_msg(text, name_sender, destination)
          print(f'E {text} de {name_sender} para {destination} através de {link_to_forward.id}')

    else:
      self.receber_mensagens(message)

  def send_msg(self, txt, source, destination):

    if source is None:
      source = self.id

    msg = { 'command_number': 99999, 'name_sender': source, 'name_destination': destination, 'text': txt }

    # print('msg pra ser enviada', msg)

    msg = json.dumps(msg).encode('utf-8')

    next_router_name = self.table.get_next_hop(destination)
    # print('nextrouter', next_router_name)
    link_to_forward = None

    for link in self.links:
      if link.id == next_router_name:
        link_to_forward = link
        break

    # print('link', link_to_forward)

    if link_to_forward is None:
      print(f'X {txt} de {source} para {destination}')
      print()
      # descartar
    else:
      print(f'E {txt} de {source} para {destination} através de {link_to_forward.id}')
      self.udp.sendto(msg, (link_to_forward.ip_addr, int(link_to_forward.port)))

  def send_table(self, ip, port):

    routes_to_announce = [{key : val for key, val in sub.items() if key != 'next'} for sub in self.table.table]

    msg = { 'command_number': 11111, 'name_sender': self.id, 'num_routes': len(self.table.table), 'routes': routes_to_announce }

    msg = json.dumps(msg).encode('utf-8')

    self.udp.sendto(msg, (ip, port))

  def init_roteamento(self):
    # print('roteamento...')
    for link in self.links:
      self.send_table(link.ip_addr, int(link.port)) #...

  def receber_mensagens(self, msg):
    id = msg[0]

    if id == 'C':
      _, ip, porto, nome = msg.split(' ')
      r = Router(nome, porto, ip)
      self.links.append(r)
      self.table.add_entry(nome, 1, nome)

    elif id == 'D':
      
      _, nome = msg.split(' ')

      to_delete = -1
      for index, link in enumerate(self.links):
        if link.id == nome:
          to_delete = index
          break

      if to_delete != -1:
        self.links.pop(to_delete)
        self.table.remove_entry(nome)
      
    elif id == 'I':
      self.stop = False
      self.timer = self.timer_f()

    elif id == 'F':

      self.stop = True

    elif id == 'T':
      
      print(self.id)
      for item in self.table.table:
        print(item['dest'], item['dist'], item['next'])
      print()

    elif id == 'E':
      
      _, txt, dest = msg.split(' ')
      # print('txt', txt, 'dest', dest)
      source = self.id

      self.send_msg(txt, source, dest)

    elif id == 'S':

      _, seconds = msg.split(' ')
      # print('dormir')
      should_change_back = False
      if self.stop == False:
        should_change_back = True

      if should_change_back:
        self.stop = True

      time.sleep(float(seconds))

      if should_change_back:
        self.stop = False
        self.timer = self.timer_f()

      # print('acordar')



def main():
  name = argv[1]
  port = argv[2]

  router = Router(name, port, local_ip)
  router.bind()
  # print(f'inicializado roteador {router.id} na porta {router.port}')

  while True:
    router.recv()

if __name__ == '__main__':
  while True:
    main()