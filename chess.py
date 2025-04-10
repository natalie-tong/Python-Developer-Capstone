import pygame
import sys

pygame.init()

width, height = 800, 800
rows, cols = 8, 8
square_size = width // rows
piece_images = {}

def load_pieces():
    """Loads chess piece images with pygame."""
    pieces = ['wp', 'bp', 'wr', 'br', 'wn', 'bn', 'wb', 'bb', 'wq', 'bq', 'wk', 'bk']
    for piece in pieces:
        piece_images[piece] = pygame.transform.smoothscale(pygame.image.load(f'icons/{piece}.png'), (square_size, square_size))

def draw_board(win, selected=None):
    """Draws chess board with pygame."""
    white = (219, 198, 153)
    black = (166, 135, 98)
    for r in range(rows):
        for c in range(cols): 
            color = white if (r + c) % 2 == 0 else black
            pygame.draw.rect(win, color, (c * square_size, r * square_size, square_size, square_size))

    if selected:
        r, c = selected
        pygame.draw.rect(win, (204, 60, 58), (c * square_size, r * square_size, square_size, square_size), 5)

def draw_pieces(win, board):
    """Draws chess pieces on the board with pygame."""
    for r in range(rows):
        for c in range(cols):
            piece = board[r][c]
            if piece != "--":
                win.blit(piece_images[piece], (c * square_size, r * square_size))

def draw_ui(win, turn, captured_pieces, check, invalid_move, game_over):
    """Draws user interface including turn, invalid move, check, and captured pieces indicators."""
    pygame.draw.rect(win, (45, 36, 30), (0, height, width, 100))
    font = pygame.font.SysFont('cambria', 24)
    red = (196, 23, 23)

    # Turn indicator
    if turn == 'w':
        if game_over:
            turn_text = "Black wins!"
        else:
            turn_text = "White's turn."
    else:
        if game_over:
            turn_text = "White wins!"
        else:
            turn_text = "Black's turn."

    text = font.render(turn_text, True, (219, 198, 153))
    win.blit(text, (25, height + 15))

    # Check indicator
    if check and not game_over:
        check_text = font.render("Check!", True, red)
        win.blit(check_text, (25, height + 50))

    # Invalid move indicator
    if invalid_move:
        invalid_text = font.render("Invalid Move!", True, red)
        win.blit(invalid_text, (175, height + 15))

    # Captured pieces indicators
    for i, piece in enumerate(captured_pieces['w']):
        win.blit(pygame.transform.smoothscale(piece_images[piece], (40, 40)), (400 + (i * 25), height + 10))
    for i, piece in enumerate(captured_pieces['b']):
        win.blit(pygame.transform.smoothscale(piece_images[piece], (40, 40)), (400 + (i * 25), height + 50))

def create_board():
    """Creates a starting chess board."""
    return [
        ["br", "bn", "bb", "bq", "bk", "bb", "bn", "br"],
        ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
        ["--", "--", "--", "--", "--", "--", "--", "--"],
        ["--", "--", "--", "--", "--", "--", "--", "--"],
        ["--", "--", "--", "--", "--", "--", "--", "--"],
        ["--", "--", "--", "--", "--", "--", "--", "--"],
        ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
        ["wr", "wn", "wb", "wq", "wk", "wb", "wn", "wr"]
    ]

def clear_path(board, start_pos, end_pos):
    """Checks that a piece's movement path is clear."""
    start_row, start_col = start_pos
    end_row, end_col = end_pos

    row_step = (end_row - start_row) // max(1, abs(end_row - start_row)) if start_row != end_row else 0
    col_step = (end_col - start_col) // max(1, abs(end_col - start_col)) if start_col != end_col else 0

    row = start_row + row_step
    col = start_col + col_step
    while (row, col) != (end_row, end_col):
        if board[row][col] != "--":
            return False
        row += row_step
        col += col_step
    return True

def valid_move(board, start_pos, end_pos, turn):
    """Checks whether a selected piece's movement is valid, including clear path checking."""
    start_row, start_col = start_pos
    end_row, end_col = end_pos
    piece = board[start_row][start_col]
    target = board[end_row][end_col]
    
    # if selected location is blank or wrong turn
    if piece == "--" or (turn == "w" and piece[0] != "w") or (turn == "b" and piece[0] != "b"):
        return False
    
    # if selected piece and target are the same
    if target != "--" and target[0] == piece[0]:
        return False
    
    piece_type = piece[1] # second index of piece name -> piece type (e.g. "wp", p = pawn)

    row_diff = abs(end_row - start_row)
    col_diff = abs(end_col - start_col)
    
    # Pawn movement check
    if piece_type == "p":
        # Forward movement
        if (col_diff == 0) and (target == "--"):  
            if (row_diff == 1):
               return True
            
            # Starting 2-step forward movement
            if (row_diff == 2) and (start_row == 6) and (board[start_row-2][start_col] == "--"): # white
                if (clear_path(board, start_pos, end_pos)):
                    return True
            if (row_diff == 2) and (start_row == 1) and (board[start_row+2][start_col] == "--"): # black
                if (clear_path(board, start_pos, end_pos)):
                    return True
            
        # Diagonal capture
        if (col_diff == 1) and (row_diff == 1) and (target != "--"): 
            return True
    
    # Rook movement check
    elif piece_type == "r":
        if (start_row == end_row) or (start_col == end_col):
            if (clear_path(board, start_pos, end_pos)):
                return True
        
    # Knight movement
    elif piece_type == "n":
        if (row_diff, col_diff) in [(2, 1), (1, 2)]:
            return True
    
    # Bishop movement check
    elif piece_type == "b":
        if (row_diff == col_diff):
            if (clear_path(board, start_pos, end_pos)):
                return True
    
    # Queen movement check
    elif piece_type == "q":
        if (start_row == end_row) or (start_col == end_col) or (row_diff == col_diff):
            if (clear_path(board, start_pos, end_pos)):
                return True
    
    # King movement check
    elif piece_type == "k":
        if (row_diff <= 1) and (col_diff <= 1):
            return True
    
    return False

def check_king(board, turn):
    """Checks if the current player's king is in check."""
    # Find king's position
    king_pos = (-1, -1)
    for r in range(rows):
        for c in range(cols):
            if board[r][c] == turn + "k":
                king_pos = (r, c)
                break
    if king_pos == (-1, -1):
        return False

    # Determine check condition
    for r in range(rows):
        for c in range(cols):
            piece = board[r][c]
            if (piece != "--") and (piece[0] != turn):
                if valid_move(board, (r, c), king_pos, piece[0]):
                    return True
    
    return False

def has_legal_moves(board, turn):
    """Determines whether the king has legal moves left on the board during check conditions."""
    for r in range(rows):
        for c in range(cols):
            if board[r][c][0] == turn:
                for r2 in range(rows):
                    for c2 in range(cols):
                        if valid_move(board, (r, c), (r2, c2), turn):
                            temp = [row[:] for row in board]
                            temp[r2][c2] = temp[r][c]
                            temp[r][c] = "--"
                            if not check_king(temp, turn):
                                return True
    return False

def main():
    win = pygame.display.set_mode((width, height + 100))
    pygame.display.set_caption("Chess")
    pygame.display.set_icon(pygame.image.load(f'icons/chess_board.png'))
    clock = pygame.time.Clock()

    load_pieces()
    board = create_board()
    captured_pieces = {'w':[], 'b':[]}
    selected = None
    turn = "w"
    running = True
    invalid_move = False
    check = False
    game_over = False

    while running:
        clock.tick(30)
        draw_board(win, selected)
        draw_pieces(win, board)
        draw_ui(win, turn, captured_pieces, check, invalid_move, game_over)
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if not game_over and event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                col, row = x // square_size, y // square_size

                if selected:
                    if (row, col) != selected:
                        piece = board[selected[0]][selected[1]]
                        if valid_move(board, selected, (row, col), turn):
                            old = board[row][col]
                            board[row][col] = piece
                            board[selected[0]][selected[1]] = "--"

                            if check_king(board, turn):
                                board[selected[0]][selected[1]] = piece
                                board[row][col] = old
                                invalid_move = True
                            else:
                                if old != "--":
                                    captured_pieces[turn].append(old)

                                turn = "b" if turn == "w" else "w"

                                check = check_king(board, turn)
                                if check and not has_legal_moves(board, turn):
                                    game_over = True

                                invalid_move = False
                        else:
                            invalid_move = True
                    selected = None
                else:
                    if board[row][col] != "--" and board[row][col][0] == turn:
                        selected = (row, col)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()