import socket

# 创建TCP客户端连接
gp6362D = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
gp6362D.connect(('192.168.1.35', 8000))

try:
    # 发送 'open "anonymous"' 命令并读取响应
    gp6362D.sendall(b'open "anonymous"\n')  # 注意添加换行符
    a = gp6362D.recv(1024).decode('utf-8').strip()  # 读取一行响应
    print(a)

    # 发送 'open ""' 命令并读取响应
    gp6362D.sendall(b'open ""\n')
    b = gp6362D.recv(1024).decode('utf-8').strip()
    print(b)

    # 发送 '*IDN?' 命令并读取响应
    gp6362D.sendall(b'*IDN?\n')
    c = gp6362D.recv(1024).decode('utf-8').strip()
    print(c)
    print("连接成功")

except socket.error as e:
    print(f"Socket错误: {e}")

gp6362D.sendall(b'*IDN?\n')
c = gp6362D.recv(1024).decode('utf-8').strip()
print(c)


gp6362D.close()