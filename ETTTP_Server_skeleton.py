import random
import tkinter as tk
from socket import *
import _thread

from ETTTP_TicTacToe_skeleton import TTT, check_msg


if __name__ == '__main__':
    global send_header, recv_header
    SERVER_PORT = 12000
    SIZE = 1024

    # TCP 소켓 생성
    server_socket = socket(AF_INET, SOCK_STREAM)

    # 생성된 소켓의 번호와 실제 address 연결
    # 주소 부분에 빈 문자열이 들어가 있는 것은 broadcast 한다는 의미
    # 12000포트에서 모든 인터페이스에 연결하도록 함
    server_socket.bind(('', SERVER_PORT))

    # 상대방의 접속 기다림
    server_socket.listen()
    MY_IP = '127.0.0.1'

    while True:
        # 대기하다가 소켓에 누군가 접속하여 연결하면 새로운 소켓과 상대방의 AF (address family) 리턴
        client_socket, client_addr = server_socket.accept()

        start = random.randrange(0, 2)  # select random to start

        ###################################################################
        # Send start move information to peer
        # start = 0 : Server , start = 1 : Client
        if start == 0:
            client_socket.send(bytes("SEND ETTTP/1.0 \r\n"
                                     + "Host: "+MY_IP+" \r\n"
                                     + "First-Move: ME \r\n\r\n", "utf-8"))
        else:
            client_socket.send(bytes("SEND ETTTP/1.0 \r\n"
                                     + "Host: "+MY_IP+" \r\n"
                                     + "First-Move: YOU \r\n\r\n", "utf-8"))

        ######################### Fill Out ################################
        # Receive ack - if ack is correct, start game
        ack = client_socket.recv(SIZE).decode()
        start_index = ack.find("A")
        end_index = ack.find(" ")
        ack = ack[:start_index] + ack[end_index + 1:]
        ack_msg = ack.split("\r\n")
        if (ack_msg[0] != ("ETTTP/1.0 ")) or (ack_msg[1] != "Host: "+str(MY_IP)+" "):
            print("프로토콜 형식에 맞지 않습니다")
            client_socket.close()
            exit()
        else:
            print("ACK received. Start the game.")

            root = TTT(client=False, target_socket=client_socket,
                       src_addr=MY_IP, dst_addr=client_addr[0])
            root.play(start_user=int(start))

            # Move `root.mainloop()` here
            root.mainloop()  # 이벤트 메시지 루프. 키보드나 마우스로부터 오는 메시지 받고 전달

            client_socket.close()

            break
    server_socket.close()
