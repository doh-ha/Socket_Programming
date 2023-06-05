"""
  ETTTP_TicTacToe_skeleton.py
 
  34743-02 Information Communications
  Term Project on Implementation of Ewah Tic-Tac-Toe Protocol
 
  Skeleton Code Prepared by JeiHee Cho
  May 24, 2023
 
"""

import random
import tkinter as tk
from socket import *
import _thread
import re
import sys

SIZE = 1024


class TTT(tk.Tk):  # TK 상속
    def __init__(self, target_socket, src_addr, dst_addr, client=True):
        super().__init__()

        self.my_turn = -1

        # 윈도우 창 크기
        self.geometry("500x800")

        self.active = "GAME ACTIVE"

        # 클라이언트 소켓
        self.socket = target_socket

        self.send_ip = dst_addr
        self.recv_ip = src_addr

        self.total_cells = 9
        self.line_size = 3

        ############## updated ###########################
        # 클라이언트는 client = True
        if client:
            self.myID = 1  # 0: server, 1: client
            # 윈도우 창 타이틀
            self.title('34743-02-Tic-Tac-Toe Client')
            # 사용자 정보
            self.user = {'value': self.line_size+1, 'bg': 'blue',
                         'win': 'Result: You Won!', 'text': 'O', 'Name': "ME"}
            # 상대방 정보
            self.computer = {'value': 1, 'bg': 'orange',
                             'win': 'Result: You Lost!', 'text': 'X', 'Name': "YOU"}
        # 서버는 client = False
        else:
            self.myID = 0
            self.title('34743-02-Tic-Tac-Toe Server')
            self.user = {'value': 1, 'bg': 'orange',
                         'win': 'Result: You Won!', 'text': 'X', 'Name': "ME"}
            self.computer = {'value': self.line_size+1, 'bg': 'blue',
                             'win': 'Result: You Lost!', 'text': 'O', 'Name': "YOU"}
        ##################################################

        # 3x3 구분선 만들기
        self.board_bg = "white"
        self.all_lines = (
            (0, 1, 2),
            (3, 4, 5),
            (6, 7, 8),
            (0, 3, 6),
            (1, 4, 7),
            (2, 5, 8),
            (0, 4, 8),
            (2, 4, 6),
        )

        self.create_control_frame()

    # quit 버튼 만들기
    def create_control_frame(self):
        """
        Make Quit button to quit game
        Click this button to exit game

        """
        # vvvvvvvvvvvvvvvvvvv  DO NOT CHANGE  vvvvvvvvvvvvvvvvvvv
        # 새로운 frame 객체 생성해서 위쪽에 배치.
        self.control_frame = tk.Frame()
        self.control_frame.pack(side=tk.TOP)

        # frame 안에 quit 버튼 생성. 버튼 누르면 quit 메소드 실행
        self.b_quit = tk.Button(
            self.control_frame, text="Quit", command=self.quit)
        self.b_quit.pack(side=tk.RIGHT)
        # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    # 상태 나타내는 frame 만들기
    # 자신이 버튼을 선택할 차례면 ready, 상대 차례면 hold 메시지를 윈도우 좌측에 출력
    def create_status_frame(self):
        """
        Status UI that shows "Hold" or "Ready"
        """
        # vvvvvvvvvvvvvvvvvvv  DO NOT CHANGE  vvvvvvvvvvvvvvvvvvv
        self.status_frame = tk.Frame()
        self.status_frame.pack(expand=True, anchor="w", padx=20)

        self.l_status_bullet = tk.Label(
            self.status_frame, text="O", font=("Helevetica", 25, "bold"), justify="left"
        )
        self.l_status_bullet.pack(side=tk.LEFT, anchor="w")
        self.l_status = tk.Label(
            self.status_frame, font=("Helevetica", 25, "bold"), justify="left"
        )
        self.l_status.pack(side=tk.RIGHT, anchor="w")
        # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    # 승패를 알려주는 메시지를 좌측 하단에 출력
    def create_result_frame(self):
        """
        UI that shows Result
        """
        # vvvvvvvvvvvvvvvvvvv  DO NOT CHANGE  vvvvvvvvvvvvvvvvvvv
        self.result_frame = tk.Frame()
        self.result_frame.pack(expand=True, anchor="w", padx=20)

        self.l_result = tk.Label(
            self.result_frame, font=("Helevetica", 25, "bold"), justify="left"
        )
        self.l_result.pack(side=tk.BOTTOM, anchor="w")
        # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    # 버튼 대신 직접 메시지 전달하는 input 창을 가장 하단에 만들기
    def create_debug_frame(self):
        """
        Debug UI that gets input from the user
        """
        # vvvvvvvvvvvvvvvvvvv  DO NOT CHANGE  vvvvvvvvvvvvvvvvvvv
        self.debug_frame = tk.Frame()
        self.debug_frame.pack(expand=True)

        self.t_debug = tk.Text(self.debug_frame, height=2, width=50)
        self.t_debug.pack(side=tk.LEFT)
        self.b_debug = tk.Button(
            self.debug_frame, text="Send", command=self.send_debug)
        self.b_debug.pack(side=tk.RIGHT)
        # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    # 보드에 버튼 만들기
    def create_board_frame(self):
        """
        Tic-Tac-Toe Board UI
        """
        # vvvvvvvvvvvvvvvvvvv  DO NOT CHANGE  vvvvvvvvvvvvvvvvvvv
        self.board_frame = tk.Frame()
        self.board_frame.pack(expand=True)

        # 개별 셀, 텍스트 값, 보드의 현재 상태, 남은 가용 가능한 움직임 확인
        self.cell = [None] * self.total_cells
        self.setText = [None] * self.total_cells
        self.board = [0] * self.total_cells
        self.remaining_moves = list(range(self.total_cells))
        # 버튼 생성
        for i in range(self.total_cells):
            self.setText[i] = tk.StringVar()
            self.setText[i].set("  ")
            self.cell[i] = tk.Label(
                self.board_frame,
                highlightthickness=1,
                borderwidth=5,
                relief="solid",
                width=5,
                height=3,
                bg=self.board_bg,
                compound="center",
                textvariable=self.setText[i],
                font=("Helevetica", 30, "bold"),
            )
            self.cell[i].bind("<Button-1>", lambda e,
                              move=i: self.my_move(e, move))
            r, c = divmod(i, self.line_size)
            self.cell[i].grid(row=r, column=c, sticky="nsew")

        # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    # 게임 초기화
    def play(self, start_user=1):
        """
        Call this function to initiate the game

        start_user: if its 0, start by "server" and if its 1, start by "client"
        """
        # vvvvvvvvvvvvvvvvvvv  DO NOT CHANGE  vvvvvvvvvvvvvvvvvvv
        self.last_click = 0

        # gui 생성 함수 호출
        self.create_board_frame()
        self.create_status_frame()
        self.create_result_frame()
        self.create_debug_frame()

        # 순서 체크하여 hold 또는 ready 상태 보여줌
        # 현재 상태를 초기화
        self.state = self.active

        # 선공이면 X표시
        if start_user == self.myID:
            self.my_turn = 1
            self.user["text"] = "X"
            self.computer["text"] = "O"
            self.l_status_bullet.config(fg="green")
            self.l_status["text"] = ["Ready"]
        # 후공이면 O 표시
        else:
            self.my_turn = 0
            self.user["text"] = "O"
            self.computer["text"] = "X"
            self.l_status_bullet.config(fg="red")
            self.l_status["text"] = ["Hold"]

            # get_move 와 별도의 스레드에서 컴퓨터의 움직임을 얻기

            _thread.start_new_thread(self.get_move, ())
        # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    def quit(self):
        """
        Call this function to close GUI
        """
        # vvvvvvvvvvvvvvvvvvv  DO NOT CHANGE  vvvvvvvvvvvvvvvvvvv
        self.destroy()
        # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    # 유효한 움직임을 입력받았을 때 send_move 를 상대에게 보냄

    def my_move(self, e, user_move):
        """
        Read button when the player clicks the button

        e: event
        user_move: button number, from 0 to 8
        """
        # vvvvvvvvvvvvvvvvvvv  DO NOT CHANGE  vvvvvvvvvvvvvvvvvvv

        # When it is not my turn or the selected location is already taken, do nothing
        if self.board[user_move] != 0 or not self.my_turn:
            return
        # Send move to peer
        valid = self.send_move(user_move)

        # If ACK is not returned from the peer or it is not valid, exit game
        if not valid:
            self.quit()

        # Update Tic-Tac-Toe board based on user's selection
        self.update_board(self.user, user_move)

        # If the game is not over, change turn
        if self.state == self.active:
            self.my_turn = 0
            self.l_status_bullet.config(fg="red")
            self.l_status["text"] = ["Hold"]
            _thread.start_new_thread(self.get_move, ())
        # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    def get_move(self):
        """
        Function to get move from other peer
        Get message using socket, and check if it is valid
        If is valid, send ACK message
        If is not, close socket and quit
        """
        ###################  Fill Out  #######################
        # 메시지를 소켓을 사용하여 받고 유효성을 확인
        # 메시지를 소켓을 사용하여 받고 유효성을 확인
        try:
            # 메시지를 소켓을 사용하여 받고 유효성을 확인
            msg = self.socket.recv(1024).decode()
            print("Read SEND message and check ETTTP")
            msg_valid_check = check_msg(msg, self.recv_ip)
            # 위치 정보 추출
            start_loc = msg.find('New-Move:') + len('New-Move:')
            end_loc = msg.find('\r\n', start_loc)
            row_col_str = msg[start_loc:end_loc]
            row, col = map(int, row_col_str.strip("()").split(","))
            loc = row * 3 + col
        except Exception as e:
            print(f"Error occurred while receiving or parsing message: {e}")
            self.socket.close()
            self.quit()
            return

        if not msg_valid_check:  # 메시지가 유효x
            self.socket.close()
            self.quit()
            return
        else:  # 메시지가 유효
            # ACK 메시지 전송
            ack_msg = f"ACK ETTTP/1.0\r\nHost:{self.send_ip}\r\nNew-Move:{row_col_str}\r\n\r\n"
            print(f"Sending ACK message: {ack_msg}")  # ACK 메시지 출력
            self.socket.send(ack_msg.encode())
            ######################################################

            # vvvvvvvvvvvvvvvvvvv  DO NOT CHANGE  vvvvvvvvvvvvvvvvvvv
            self.update_board(self.computer, loc, get=True)
            if self.state == self.active:
                self.my_turn = 1
                self.l_status_bullet.config(fg="green")
                self.l_status["text"] = ["Ready"]
            # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    # debug로 메시지 보내기
    def send_debug(self):
        """
        Function to send message to peer using input from the textbox
        Need to check if this turn is my turn or not
        """

        if not self.my_turn:
            self.t_debug.delete(1.0, "end")
            return
        # get message from the input box
        d_msg = self.t_debug.get(1.0, "end")
        d_msg = d_msg.replace(
            "\\r\\n", "\r\n"
        )  # msg is sanitized as \r\n is modified when it is given as input
        self.t_debug.delete(1.0, "end")

        ###################  Fill Out  #######################

        # 1. 해당 자리가 이미 선점되지 않았는지 확인
        # 메시지에서 움직임을 추출
        start_index = d_msg.find("(")
        end_index = d_msg.find(")")
        location = d_msg[start_index + 1: end_index]
        # 행 인덱스
        row = int(location[0])
        # 열 인덱스
        col = int(location[2])
        # 둘이 더한 게 user_move
        user_move = row*3 + col
        print("열,행: " + str(row)+","+str(col))
        # 유효한 자리인지 확인
        if self.board[user_move] != 0:  # 0으로 초기화했는데 0이 아니라는 건 이미 차지된 자리라는 뜻
            print("유효하지 않은 칸입니다.")
            return

        # 2. 상대방에게 메시지 전달
        self.socket.send(bytes(d_msg, "utf-8"))  # 디버그 창에 입력한 걸 보내야 하니까
        print("Generate ETTTP SEND message and send to peer")

        # 3. 상대방에게 메시지 받기 & ETTTP 프로토콜 확인
        rcv_msg = self.socket.recv(SIZE).decode()
        if check_msg(rcv_msg, self.recv_ip):
            # Mark on tic-tac-toe board
            # update_board에서 보드판 바뀌게 하기 위한 변수
            loc = user_move  # peer's move, from 0 to 8
            print("Read ACK message and check ETTTP")
            # 상대편에서는 get_move에서 업데이트

        ######################################################

        # vvvvvvvvvvvvvvvvvvv  DO NOT CHANGE  vvvvvvvvvvvvvvvvvvv
        # 4. 움직임 업데이트
        self.update_board(self.user, loc)

        if self.state == self.active:  # always after my move
            self.my_turn = 0
            self.l_status_bullet.config(fg="red")
            self.l_status["text"] = ["Hold"]
            _thread.start_new_thread(self.get_move, ())

        # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    def send_move(self, selection):
        """
        Function to send message to peer using button click
        selection indicates the selected button
        """

        row, col = divmod(selection, 3)
        ###################  Fill Out  #######################
        # 버튼의 입력값으로 상대에게 메시지 보냄
        if self.board[selection] != 0:
            print("유효하지 않은 칸입니다.")
            return False
        else:
            msg = f"SEND ETTTP/1.0\r\nHost:{self.send_ip}\r\nNew-Move:({row},{col})\r\n\r\n"
            self.socket.send(bytes(msg, "utf-8"))

        # ACK 받아옴
        ack = self.socket.recv(1024).decode()
        if check_msg(ack, self.recv_ip):
            return True
        else:
            return False
        ######################################################

    def check_result(self, winner, get=False):
        """
        Function to check if the result between peers are same
        get: if it is false, it means this user is winner and need to report the result first
        """
        if not get:
            # 이 사용자가 승자인 경우 결과를 먼저 보고해야 함
            result = "YOU" if winner == self.user else "ME"
            message = f"SEND ETTTP/1.0\r\nHost:{self.src_addr}\r\nWinner: {result}\r\n\r\n"
            self.socket.send(message.encode())
        else:
            # 상대편의 결과 수신
            recv_msg = self.socket.recv(1024).decode().split("\r\n")

            # 상대방이 보낸 결과가 정확한지 확인
            if len(recv_msg) < 4 or recv_msg[0] != "SEND ETTTP/1.0" or f"Host:{self.dst_addr}" not in recv_msg[1] or "Winner: " not in recv_msg[2]:
                print("프로토콜 형식에 맞지 않습니다")
                return False

            peer_result = recv_msg[2].split(": ")[1]

            if (winner == self.user and peer_result != "YOU") or (winner != self.user and peer_result != "ME"):
                return False

            # 패자인 경우 결과를 보고함
            result = "YOU" if winner == self.user else "ME"
            message = f"ACK ETTTP/1.0\r\nHost:{self.src_addr}\r\nWinner: {result}\r\n\r\n"
            self.socket.send(message.encode())

            # 승리 혹은 패배를 출력
            if result == "YOU":
                print("You Win")
            else:
                print("You Lose")

        return True

    # vvvvvvvvvvvvvvvvvvv  DO NOT CHANGE  vvvvvvvvvvvvvvvvvvv

    def update_board(self, player, move, get=False):
        """
        This function updates Board if is clicked
        """
        self.board[move] = player["value"]
        self.remaining_moves.remove(move)
        self.cell[self.last_click]["bg"] = self.board_bg
        self.last_click = move
        self.setText[move].set(player["text"])
        self.cell[move]["bg"] = player["bg"]
        self.update_status(player, get=get)

    def update_status(self, player, get=False):
        """
        This function checks status - define if the game is over or not
        """
        winner_sum = self.line_size * player["value"]
        for line in self.all_lines:
            if sum(self.board[i] for i in line) == winner_sum:
                self.l_status_bullet.config(fg="red")
                self.l_status["text"] = ["Hold"]
                self.highlight_winning_line(player, line)
                correct = self.check_result(player["Name"], get=get)
                if correct:
                    self.state = player["win"]
                    self.l_result["text"] = player["win"]
                else:
                    self.l_result["text"] = "Somethings wrong..."

    def highlight_winning_line(self, player, line):
        """
        This function highlights the winning line
        """
        for i in line:
            self.cell[i]["bg"] = "red"

    # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


# End of Root class


def check_msg(msg, recv_ip):
    """
    Function that checks if received message is ETTTP format
    """

    # 프로토콜 형식 검토
    if len(msg) > 0:
        if msg[0] == "A":  # ACK
            protocol = "ACK"
        elif msg[0] == "S":  # SEND
            protocol = "SEND"
    else:
        print("메시지에 내용이 없습니다")
        quit()
    lines = msg.split("\r\n")

    # ETTTP 체크
    if lines[0] != (protocol + " ETTTP/1.0") or lines[1] != ("Host:" + recv_ip):
        print("프로토콜 구조에 맞지 않습니다")
        quit()

    return True
