from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from fastapi.responses import StreamingResponse
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
import json
from langchain.callbacks.manager import CallbackManager
from llama_cpp import Llama

# Define the data models
class Message(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    messages: List[Message]
    temperature: Optional[float] = 1.0
    max_tokens: Optional[int] = 1024
    stream: Optional[bool] = True

# Initialize FastAPI app and Llama model
app = FastAPI()
callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
llm = Llama(
    model_path=r"D:\Kuliah Telkom University\Project\Tubes Sister\Models\llama-2-7b-function-calling.Q3_K_M.gguf",
    callback_manager=callback_manager,
    n_gpu_layers=30,
    n_ctx=4096,
    n_batch=512,
    n_threads=4,
    verbose=True
)

import time

@app.get("/stream-test")
async def stream_test():
    def generate_numbers():
        for i in range(10):
            yield f"Number: {i}\n"
            time.sleep(1)  # Simulate delay

    return StreamingResponse(generate_numbers(), media_type="text/plain")

@app.post("/chat")
async def chat_completions(request: ChatCompletionRequest):
    try:
        messages_dict = [message.dict() for message in request.messages]
        for message_data in messages_dict:
            print(message_data)
            print("")
        def token_generator():

            for token in llm.create_chat_completion(
                stream=True,
                messages=messages_dict,
                temperature=request.temperature,
                max_tokens=request.max_tokens,  
            ):
                content = token['choices'][0]['delta'].get('content')
                status = token['choices'][0]["finish_reason"]
      
                if content is not None:
                    print(content, end="", flush=True)
                    yield content

        if request.stream:
            
            return StreamingResponse(token_generator(), media_type="text/plain")
        else:
            response = llm.create_chat_completion(
                stream=False,
                messages=messages_dict,
                temperature=request.temperature,
                max_tokens=request.max_tokens
            )
            return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the API with Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8080)
