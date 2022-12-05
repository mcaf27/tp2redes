import socket, json, threading
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

  def bind(self):
    self.udp = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    print(self.ip_addr, self.port, self.id)
    self.udp.bind((self.ip_addr, int(self.port)))

  def recv(self):
    print(f'{self.id} vai receber mensagens')
    msg, addr = self.udp.recvfrom(buffer_size)
    msg = msg.decode('utf-8')
    print(f'recebida por {self.id}:', msg)
    # atualiza tabela

  def send_msg(self, msg, ip, port):
    msg = msg.encode('utf-8')
    self.udp.sendto(msg, (ip, port))
    # encaminhar de acordo com a tabela de rotas

  def send_table(self, ip, port):
    msg = json.dumps(self.table.table).encode('ascii')
    self.udp.sendto(msg, (ip, port))
    print(f'enviando {self.id}:', self.table)

  def init_roteamento(self):
    print(f'links de {self.id}', self.links)
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
      print(f'{self.id} vai iniciar roteamente')
      t = threading.Timer(1, self.init_roteamento)
      t.start()

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