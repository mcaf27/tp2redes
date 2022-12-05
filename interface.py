from router import Router

r1_port = 8000
r2_port = 8001

local_ip = '127.0.0.1'

# r1 = Router('roteador1', r1_port)
# r2 = Router('roteador2', r2_port)

# r1.bind()
# r2.bind()

# r2.send(r1_port)
# r1.recv()

routers = []

def get_router(ip, porto):
  for router in routers:
    if router.ip_addr == ip and router.port == porto:
      return router

# comandos

def send_message():
  while True:
    try:
      in_ = input()
      ip1, porto1, x = in_.split(' ')[:3]

      if ip1 == 'x':
        ip1 = local_ip

      r = get_router(ip1, porto1)
      i = 0
      if (r == None):
        r = Router(f'roteador{i}', porto1, ip1)
        routers.append(r)
      
      if x == 'C':
        ip2, porto2, nome = in_.split(' ')[3:]
        if ip2 == 'x':
          ip2 = local_ip
        
        r2 = Router(nome, porto2, ip2)
        routers.append(r2)
        print('---', nome, porto2, ip2, routers)

        r.receber_mensagens(f'C {ip2} {porto2} {nome}')

      elif x == 'D':
        ip2, porto2 = in_.split(' ')[3:]
        # tá correto assim no enunciado mesmo?
        r2 = get_router(ip2, porto2)
        nome = r2.id
        r.receber_mensagens(f'D {nome}')

      elif x == 'I':
        r.receber_mensagens('I')

      elif x == 'F':
        r.receber_mensagens('F')

      elif x == 'T':
        r.receber_mensagens('T')

      elif x == 'E':
        txt, dest = in_.split(' ')[3:]
        r.receber_mensagens(f'E {txt} {dest}')

    except ValueError:
      print('comando inválido')
      continue


send_message()