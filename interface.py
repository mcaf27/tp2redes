from router import Router

r1_port = 8000
r2_port = 8001

r1 = Router('roteador1', r1_port)
r2 = Router('roteador2', r2_port)

r1.bind()
r2.bind()

r2.send(r1_port)
r1.recv()

routers = []

def get_router(ip, porto):
  for router in routers:
    if router.ip_addr == ip and router.port == porto:
      return router

# comandos

def send_message():
  # ler do stdin para mandar as mensagens que vão ser lidas nos roteadores
  pass