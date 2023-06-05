'''
  ETTTP_Client_skeleton.py
 
  34743-02 Information Communications
  Term Project on Implementation of Ewah Tic-Tac-Toe Protocol
 
  Skeleton Code Prepared by JeiHee Cho
  May 24, 2023
 
 '''

import random
import tkinter as tk
from socket import *
import _thread

from ETTTP_TicTacToe_skeleton import TTT, check_msg


if __name__ == '__main__':

    SERVER_IP = '127.0.0.1'
    MY_IP = '127.0.0.1'
    SERVER_PORT = 12000
    SIZE = 1024
    SERVER_ADDR = (SERVER_IP, SERVER_PORT)

    # TCP 소켓 생성
    # 첫 번쨰 인자는 IPv4, 두 번쨰 인자는 소켓 타입을 의미

    with socket(AF_INET, SOCK_STREAM) as client_socket:
        # 서버 소켓과 연결
        client_socket.connect(SERVER_ADDR)

        ###################################################################
        # Receive who will start first from the server
        # 누가 먼저 시작할지 서버에서 계산한 결과를 받아옴. byte를 문자열로 변환하여 읽음
        start = client_socket.recv(SIZE).decode()

        ######################### Fill Out ################################
        # Send ACK
        # 서버에 ACK 전송. 문자열을 byte로 변환하여 인코딩
        client_socket.send("ACK".encode())
        ###################################################################

        # Start game

        root = TTT(target_socket=client_socket,
                   src_addr=MY_IP, dst_addr=SERVER_IP)
        root.play(start_user=int(start))
        root.mainloop()  # 이벤트 메시지 루프. 키보드나 마우스로부터 오는 메시지 받고 전달
        client_socket.close()  # 소켓 종료
