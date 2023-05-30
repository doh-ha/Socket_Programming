import socket
import threading  # 사실 스레드 필요없음


class TicTacToe:
    def __init__(self):
        self.board = [[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]]
        self.turn = "X"  # x 부터 시작
        self.you = "X"  # 호스트가 X
        self.opponent = "O"  # 초대받은 사람이 O
        self.winner = None
        self.game_over = False

        self.counter = 0  # 모든 칸이 채워져 있으면 동점

    def host_game(self, host, port):  # 플레이어1
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP 소켓 열기
        server.bind((host, port))  # 튜플로 합치기
        server.listen(1)

        client, addr = server.accept()

        self.you = "X"
        self.opponent = "O"
        threading.Thread(target=self.handle_connection, args=(client,)).start()
        server.close()  # 하나의 플레이어와만 연결되면 됨

    def connect_to_game(self, host, port):  # 플레이어2
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP 소켓 열기
        client.connect((host, port))

        self.you = "O"
        self.opponent = "X"
        threading.Thread(target=self.handle_connection, args=(client,)).start()

    def handle_connection(self, client):
        while not self.game_over:  # 게임 종료 안 되었다면
            if self.turn == self.you:  # 내 차례
                move = input("Enter a move (row, column): ")  # move 할 수 있는 기회
                if self.check_valid_move(move.split(',')):  # move가 유효한지 확인
                    # move 실행. 나의 움직임으로 만들기
                    self.apply_move(move.split(','), self.you)
                    self.turn = self.opponent  # 순서 넘어감
                    client.send(move.encode('utf-8'))  # 상대방에게 보내기
                else:
                    print("Invalid move!")
            else:
                data = client.recv(1024)  # 1024짜리 데이터 받기
                if not data:  # 데이터 없으면
                    break

                else:
                    self.apply_move(data.decode('utf-8').split(','),
                                    self.opponent)  # 데이터 받아서 해독
                    self.turn = self.you  # 다시 나의 차례
        client.close()

    def apply_move(self, move, player):  # 움직임 적용
        if self.game_over:  # 게임 끝났으면 return
            return
        self.counter += 1  # 채워진 칸 수 카운트
        # 입력 받은 좌표 값을 player의 값으로 받음
        self.board[int(move[0])][int(move[1])] = player
        self.print_board()  # ui 보여주기

        if self.check_if_won():  # 승자가 있는지 확인
            if self.winner == self.you:  # 내가 이김
                print("You win!")
                exit()
            elif self.winner == self.opponent:  # 내가 짐
                print("You lose!")
                exit()
        else:  # 승자가 없으면
            if self.counter == 9:  # 칸이 다 차서 동점
                print("It is a tie!")
                exit()

    def check_valid_move(self, move):  # 움직임이 유효한가
        # 해당 영역이 빈칸인지 불린 값을 리턴
        return self.board[int(move[0])][int(move[1])] == " "

    def check_if_won(self):  # 승자가 있는가 -> 빙고가 만들어졌는가
        for row in range(3):  # 가로
            # 빈 칸이 아니고 모두 같은 숫자인가
            if self.board[row][0] == self.board[row][1] == self.board[row][2] != " ":
                # 해당 영역에 있는 symbol을 가진 플레이어가 승자
                self.winner = self.board[row][0]
                self.game_over = True  # 게임을 종료해도 됨
                return True  # 승자가 있음

        for col in range(3):
            if self.board[0][col] == self.board[1][col] == self.board[2][col] != " ":
                # 해당 영역에 있는 symbol을 가진 플레이어가 승자
                self.winner = self.board[0][col]
                self.game_over = True  # 게임을 종료해도 됨
                return True  # 승자가 있음

        if self.board[0][0] == self.board[1][1] == self.board[2][2] != " ":
            # 해당 영역에 있는 symbol을 가진 플레이어가 승자
            self.winner = self.board[0][0]
            self.game_over = True  # 게임을 종료해도 됨
            return True  # 승자가 있음

        if self.board[0][2] == self.board[1][1] == self.board[2][0] != " ":
            # 해당 영역에 있는 symbol을 가진 플레이어가 승자
            self.winner = self.board[0][2]
            self.game_over = True  # 게임을 종료해도 됨
            return True  # 승자가 있음

        return False

    def print_board(self):  # ui 출력
        for row in range(3):
            print(" | ". join(self.board[row]))
            if row != 2:  # 마지막 줄이 아니면 구분선 출력
                print("-------------")


game = TicTacToe()
game.connect_to_game('localhost', 9999)
