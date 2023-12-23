def get_total_token(chats_list: list):
    total_token = 0

    for msg in chats_list:
        # Simple approximation by splitting the content by spaces
        # This will count words and punctuation as separate tokens
        tokens = msg['content'].split()
        total_token += len(tokens)

    return total_token

def chat_summary(chats_list : list, chat_summary, cached_chat : list):
    cached_chat.append(chats_list)
    chats_list = []
    chats_list.append({'role' : 'assistant', 'content' : f"Here is the chat summary : \n{chat_summary}"})
    return chats_list, cached_chat