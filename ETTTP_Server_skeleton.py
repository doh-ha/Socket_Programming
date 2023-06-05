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
        client_socket.send(str(start).encode())

        ######################### Fill Out ################################
        # Receive ack - if ack is correct, start game
        ack = client_socket.recv(SIZE).decode()
        if check_msg(ack, client_addr):
            print("ACK received. Start the game.")

            ###################################################################

            root = TTT(client=False, target_socket=client_socket,
                       src_addr=MY_IP, dst_addr=client_addr[0])
            root.play(start_user=int(start))

            # Move `root.mainloop()` here
            # 이벤트 메시지 루프. 키보드나 마우스로부터 오는 메시지 받고 전달
            root.mainloop()

            # 소켓 종료. 연결 끊기
            client_socket.close()

            break

        else:
            print("No ACK received. Check the client.")
    server_socket.close()
