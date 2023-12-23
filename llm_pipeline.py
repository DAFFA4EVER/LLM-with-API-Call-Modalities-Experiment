def llm_pipeline(user_input, system_prompt, assistant_prompt, agent_tools_prompt, chats_list, stream_output : bool, temperature, max_tokens=-1, url="http://localhost:8080/chat", agent='normal'): 
    import requests
    import json
    from get_model_output import get_model_output

    from datetime import datetime

    # Getting the current date and time
    current_time = datetime.now()

    # Define the URL and the header

    headers = {"Content-Type": "application/json"}

    messages : list = chats_list.copy()

    #print(chats_list)
    #print(user_input)
    
    print_output = True

    if(agent == 'normal'):    
        messages.append(
            {
                    "role": "system",
                    "content": system_prompt,
                },
        )

        messages.append(
            {
                    "role": "user",
                    "content": user_input,
                },
        )
    
    elif(agent == 'summarize'):
        print_output = False
        messages.append(
            {
                    "role": "system",
                    "content": "You are an AI specializes in summarization. You always highlight the important part and details in a conversation to avoid knowledge gaps.",
                },
        )
        messages.append(
            {
                    "role": "user",
                    "content": f"""Please summarize the chat or our conversation into bullet point:\n{str(messages)}""" ,
                },
        )
    elif(agent == 'context'):
        messages.append(
            {
                    "role": "assistant",
                    "content": assistant_prompt,
                },
        )
    
    elif(agent == 'tools'):
        #print(agent_tools_prompt)
        messages.append(
            {
                    "role": "system",
                    "content": agent_tools_prompt,
                },
        )
        messages.append(
            {
                    "role": "user",
                    "content": user_input,
                },
        )
    elif(agent == 'tools_return'):
        messages.append(
            {
                    "role": "system",
                    "content": f"The result of user request about ({user_input}) is:\n({str(assistant_prompt)})\n\nFor context, today is {current_time}. Use natural response to explain it!",
                },
        )
        messages.append(
                {
                        "role": "user",
                        "content": f"Could you tell me a summary about it?",
                    },
            )
    
    # Define the data payload
    data = {
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": stream_output
    }

    #if(agent == 'tools'):
    #    for msg in messages:
    #        if((msg['role'] == "system") and (msg['content'] == agent_tools_prompt)):
    #            messages.remove(msg)

    #        if((msg['role'] == "user") and (user_input in msg['content'])):
    #            messages.remove(msg)

    # Post the request and get the response object
    response = requests.post(url, headers=headers, data=json.dumps(data), stream=stream_output)

    text_output, token_count = get_model_output(stream_output=stream_output, response=response, print_output=print_output, response_type=agent)

    return text_output, token_count