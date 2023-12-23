def chat_management(user_input, model_output, system_output, chat_list : list, mode='normal'):
    """
    Appending user_input and model_output to the chat_list
    """

    from datetime import datetime

    # Getting the current date and time
    current_time = datetime.now()

    if(mode != "tools"):
        chat_list.append(
            {
                        "role": "user",
                        "content": user_input,
                    })
        chat_list.append(
            {
                        "role": "assistant",
                        "content": model_output,
                    })

    else:
        chat_list.append(
            {
                        "role": "assistant",
                        "content": f"""{system_output}""",
                    })

    return chat_list