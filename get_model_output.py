def get_model_output(stream_output, response, print_output : bool, response_type="normal"):
    import json

    is_func = False

    token_count = 0

    output_text = ""
    if stream_output:
        # Handling streaming response
        if response.status_code == 200:
            output_text = ""
            try:
                for line in response.iter_content(decode_unicode=True):
                    #print(line.decode('utf-8'), end="", flush=True)
                    line_str = line

                    output_text += line_str
                    token_count += 1
                    if((("FUNC_CALL" in output_text) or ("use_func" in output_text)) and (response_type == "tools")):
                        if(is_func == False):
                            print("\n\nPerforming your request. Please wait...🔃\n\n", end="")
                            is_func = True
                    else:
                        if(print_output):
                            print(line_str, end="", flush=True)

            except Exception as e:
                print("---------------------------------------------------------")
                print("An error occurred:", e)
            finally:
                pass
                #print("Final Output Text:")
                #print(output_text)
        else:
            print("---------------------------------------------------------")
            print("Error:")
            print(response.status_code, response.text)
    else:
        # Handling non-streaming response
        if response.status_code == 200:
            #print("Success:")
            try:
                json_data = json.loads(response.text)
                choices = json_data.get("choices", [])
                output_text = "".join(choice.get("message", {}).get("content", "") for choice in choices if choice.get("message"))
                #print("Final Output Text:")

                if((("FUNC_CALL" in output_text) or ("use_func" in output_text))):
                    print("\nPerforming your request. Please wait...🔃\n")
                else:
                    print(output_text)

                token_count = json_data.get("usage")['total_tokens']
            except json.JSONDecodeError as e:
                print("Error decoding JSON:", e)
            except Exception as e:
                print("An error occurred:", e)
        else:
            print("Error:")
            print(response.status_code, response.text)

    return output_text, token_count