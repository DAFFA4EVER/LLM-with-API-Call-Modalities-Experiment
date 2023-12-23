import pygame
import chess
import sys

# Constants
SQUARE_SIZE = 75  # This is the size of each square on the board

import requests
import json

chess_prompt = """As an AI chess bot, your role is to engage with users in the context of a chess game. When a user makes a move or asks a question, your task is to respond thoughtfully and informatively. Your responses should not only provide the next move but also give reasons for that move, reflecting a strategic understanding of the game. You should adhere to the given JSON schema for your responses, which includes the fields "color", "piece", "move", "reason", and "role". The "color" field will be either "white" or "black", representing the color of the piece you are moving. The "piece" field will denote the type of the piece (e.g., "Pawn", "Knight", "Bishop", "Rook", "Queen", "King"). The "move" field should describe the move you want to make, in standard chess notation (e.g., "e4", "Nf3", "Bb5"). In the "reason" field, provide an explanation for why you are making the move, which could include strategic advantages, defensive tactics, or other game-theoretical considerations. Lastly, the "role" will always be "chess_bot", indicating the function you are performing.

Remember, each interaction with a user is a chance to exhibit your chess knowledge and to make the game engaging and educational. Please make a move as white. Good luck, and make your moves count!"""

# Initialize an empty list to store the history of interactions
interaction_history = []

def update_interaction_history(role, content):
    global interaction_history
    # Add the new interaction
    interaction_history.append({"role": role, "content": content})
    # Ensure only the last 5 interactions are kept
    if len(interaction_history) > 5:
        interaction_history = interaction_history[-5:]

def send_move_to_chatbot(chess_prompt, user_piece_move, pieces_coordinate):
    global interaction_history
    url = "http://localhost:8080/chat"
    
    # Prepare the new user interaction
    user_interaction = {
        "role": "user",
        "content": {
            "role": "user", 
            "piece": user_piece_move[0], 
            "move": user_piece_move[1], 
            "pieces_coordinate": pieces_coordinate
        }
    }

    # Update the history with the new interaction
    update_interaction_history("user", user_interaction["content"])

    # Prepare the move data including the history
    move_data = {
        "messages": interaction_history + [{"role": "system", "content": chess_prompt}, user_interaction],
        "temperature": 0.7,
        "max_tokens": -1,
        "stream": False
    }

    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, json=move_data, headers=headers)
    if response.status_code == 200:
        # Extract the assistant's response and update the history
        assistant_response = response.json()
        update_interaction_history("assistant", assistant_response)
        return assistant_response
    else:
        print("Failed to get response from the chatbot")
        return None

def extract_json_from_response(response_text):
    start_index = response_text.find('{')
    end_index = response_text.rfind('}') + 1
    json_string = response_text[start_index:end_index]
    return json.loads(json_string)

def make_bot_move(board, move_data):
    try:
        move = chess.Move.from_uci(move_data["move"])
        if move in board.legal_moves:
            board.push(move)
        else:
            print("Received an illegal move from the chatbot")
    except ValueError:
        print("Received an invalid move format from the chatbot")

# Load images
def load_images():
    pieces = ["P", "N", "B", "R", "Q", "K"]
    colors = ["w", "b"]
    images = {}
    for piece in pieces:
        for color in colors:
            filename = f"{color}_{piece}.png"
            path = f"Modalities/Chess/images/{filename}"
            try:
                # Load the image from the path
                image = pygame.image.load(path)
                # Scale the image to fit the square size
                images[f"{color}_{piece}"] = pygame.transform.scale(image, (SQUARE_SIZE, SQUARE_SIZE))
            except FileNotFoundError:
                print(f"Could not find the image {path}")
                # Handle the missing file appropriately
    return images

# Draw board and pieces
def draw_board(screen):
    colors = [pygame.Color("white"), pygame.Color("gray")]
    for row in range(8):
        for col in range(8):
            color = colors[(row + col) % 2]
            pygame.draw.rect(screen, color, pygame.Rect(col*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def draw_pieces(screen, board, images):
    for row in range(8):
        for col in range(8):
            piece = board.piece_at(chess.square(col, row))
            if piece:
                color = 'w' if piece.color == chess.WHITE else 'b'
                piece_key = f"{color}_{piece.symbol().upper()}"
                try:
                    screen.blit(images[piece_key], pygame.Rect(col*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
                except KeyError:
                    print(f"No image for piece key: {piece_key}")
                    # Handle the KeyError appropriately

# Helper function to convert pixels to board position
def pixel_to_board_pos(pixel_x, pixel_y):
    return (pixel_x // SQUARE_SIZE, pixel_y // SQUARE_SIZE)

# Initialize Pygame and load images
pygame.init()
images = load_images()

# Set up the display
size = (600, 600)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Chess Game")

# Initialize the chess board
board = chess.Board()

# Store the state of the selected piece and its original square
selected_piece = None
selected_square = None

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:

            col, row = pixel_to_board_pos(*event.pos)
            square = chess.square(col, row)
            piece = board.piece_at(square)
            if selected_piece is None and piece is not None and piece.color == chess.BLACK:
                selected_piece = piece
                selected_square = square
            elif selected_piece is not None:
                print("Selected Piece:", selected_piece)
                print("Selected Square:", chess.square_name(selected_square))
                print("Legal Moves:", list(board.legal_moves))
                move = chess.Move(selected_square, square)
                if move in board.legal_moves:
                    board.push(move)
                    # Prepare chess prompt and move data
                    user_piece_move = [str(selected_piece), str(move)]
                    pieces_coordinate = [{"piece": str(piece), "coordinate": str(square)}
                                         for square in chess.SQUARES
                                         for piece in [board.piece_at(square)] if piece]

                    response = send_move_to_chatbot(chess_prompt=chess_prompt, user_piece_move=user_piece_move, pieces_coordinate=pieces_coordinate)
                    if response:
                        bot_move_data = extract_json_from_response(response)
                        make_bot_move(board, bot_move_data)

                    selected_piece = None
                    selected_square = None

    # Draw the board and pieces
    draw_board(screen)
    draw_pieces(screen, board, images)

    # Highlight the selected square
    if selected_square is not None:
        highlight_color = pygame.Color(255, 255, 0, 128)
        col, row = chess.square_file(selected_square), chess.square_rank(selected_square)
        highlight_rect = pygame.Rect(col*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
        pygame.draw.rect(screen, highlight_color, highlight_rect)

    # Update the display
    pygame.display.flip()


# Quit Pygame
pygame.quit()