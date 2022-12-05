import socket, json, threading
from sys import argv

local_ip = '127.0.0.1'
buffer_size = 1024

def timer(init):

  def f():
    init()
    timer(init)
  
  thread = threading.Timer(1, f)
  thread.start()
  return thread

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

class Router:
  def __init__(self, id, port, ip=local_ip):
    self.id = id
    self.ip_addr = ip
    self.port = port
    self.table = RouterTable(id, 0, id)
    self.udp = None
    self.links = []

  def __eq__(self, obj):
    if isinstance(obj, Router):
      return self.id == obj.id
    return  self.id == obj

  def __repr__(self):
    return f'{self.id}:{self.ip_addr}/{self.port}'

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
    print(self.ip_addr, self.port, self.id)
    self.udp.bind((self.ip_addr, int(self.port)))

  def recv(self):
    msg, addr = self.udp.recvfrom(buffer_size)
    msg = msg.decode('utf-8')

    msg = json.loads(msg)

    command_number = msg.get('command_number')
    name_sender = msg.get('name_sender')
    routes = msg.get('routes')
    message = msg.get('message')

    if command_number == 11111:
      self.update_table(routes, name_sender)
    
    # mensagem de texto

    else:
      print(f'processando a mensagem {message}...')
      self.receber_mensagens(message)

  def send_msg(self, msg, ip, port):

    short_int = '99999'

    msg = (short_int + msg).encode('utf-8')
    self.udp.sendto(msg, (ip, port))
    # encaminhar de acordo com a tabela de rotas

  def send_table(self, ip, port):

    routes_to_announce = [{key : val for key, val in sub.items() if key != 'next'} for sub in self.table.table]

    msg = { 'command_number': 11111, 'name_sender': self.id, 'num_routes': len(self.table.table), 'routes': routes_to_announce }

    msg = json.dumps(msg).encode('utf-8')

    self.udp.sendto(msg, (ip, port))

  def init_roteamento(self):
    print('iniciou roteamento')
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
      i = self.links(nome)
      self.links.pop(i)
      self.table.remove_entry(nome)

    elif id == 'I':
      timer(self.init_roteamento)

    elif id == 'F':

      # mandar mensagens que sua distância é infinita
      
      pass

    elif id == 'T':
      
      print('***', self.id, '***')
      for item in self.table.table:
        print('\t', item['dest'], item['dist'], item['next'])
      print('---')

    elif id == 'E':
      
      _, txt, dest = msg.split(' ')
      print('E', txt, 'de', self.id, 'para', dest)
      print()

      # encaminhar...

def main():
  name = argv[1]
  port = argv[2]

  router = Router(name, port, local_ip)
  router.bind()
  print(f'inicializado roteador {router.id} na porta {router.port}')

  while True:
    router.recv()

if __name__ == '__main__':
  while True:
    main()