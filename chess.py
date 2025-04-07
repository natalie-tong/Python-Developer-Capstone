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
        piece_images[piece] = pygame.transform.smoothscale(pygame.image.load(f'images/{piece}.png'), (square_size, square_size))

def draw_board(win):
    """Draws chess board with pygame."""
    white = (219, 198, 153)
    black = (166, 135, 98)
    for r in range(rows):
        for c in range(cols):
            color = white if (r + c) % 2 == 0 else black
            pygame.draw.rect(win, color, (c * square_size, r * square_size, square_size, square_size))

def draw_pieces(win, board):
    """Draws chess pieces on the board with pygame."""
    for r in range(rows):
        for c in range(cols):
            piece = board[r][c]
            if piece != "--":
                win.blit(piece_images[piece], (c * square_size, r * square_size))

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

    row, col = start_row + row_step, start_col + col_step
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
    
    # King movement
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
                if valid_move(board, (r, c), king_pos, turn):
                    return True
    
    return False

def main():
    win = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Chess")
    pygame.display.set_icon(pygame.image.load(f'images/chess_board.png'))
    clock = pygame.time.Clock()
    board = create_board()
    load_pieces()
    running = True
    selected_piece = None
    turn = "w"

    while running:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                col, row = x // square_size, y // square_size
                if selected_piece:
                    if valid_move(board, selected_piece, (row, col), turn):
                        board[row][col] = board[selected_piece[0]][selected_piece[1]]
                        board[selected_piece[0]][selected_piece[1]] = "--"
                        
                        turn = "b" if turn == "w" else "w"

                    selected_piece = None
                else:
                    if (board[row][col] != "--") and (board[row][col][0] == turn):
                        selected_piece = (row, col)

        draw_board(win)
        draw_pieces(win, board)
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()