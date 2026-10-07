# chat.py
from agent import run_agent

history = []

while True:
    q = input("You: ").strip()
    if q.lower() in ("quit", "exit"):
        break
    print("Agent:", run_agent(q, messages=history))