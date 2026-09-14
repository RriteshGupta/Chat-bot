from langchain_ollama import ChatOllama

llm = ChatOllama(model="llama3.1")


while True:
  user_input = input('you : ')
  if user_input == 'exit':
    break
  print("Ai : ")
  for chunk in llm.stream(user_input):
    print(chunk.content,end="",flush=True) 
  print(" ")