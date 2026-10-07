# agent.py
from weather_tool import get_forecast

TOOLS = {"get_forecast": get_forecast}

def fake_llm(messages):
    """Pretends to be Bedrock. Replace this later with a real converse() call."""
    last = messages[-1]

    # Turn 1: user asked something -> request one tool call per city
    if last["role"] == "user" and "text" in last["content"][0]:
        text = last["content"][0]["text"].strip("?.! ")
        if " and " in text:
            left, right = text.split(" and ", 1)
            cities = [left.split()[-1], right.split()[0]]
        else:
            cities = [text.split()[-1]]

        blocks = [
            {"toolUse": {"toolUseId": f"t{i}", "name": "get_forecast",
                         "input": {"city": c}}}
            for i, c in enumerate(cities)
        ]
        return {"stopReason": "tool_use",
                "message": {"role": "assistant", "content": blocks}}

    # Turn 2: all tool results are back -> write one answer
    lines = []
    for block in last["content"]:
        result = block["toolResult"]["content"][0]["json"]
        if "error" in result:
            lines.append(f"Sorry, {result['error']}")
        else:
            day = result["forecast"][0]
            lines.append(f"{result['city']}: {day['min_c']}-{day['max_c']}°C "
                         f"on {day['date']}, rain {day['rain_mm']} mm.")
    return {"stopReason": "end_turn",
            "message": {"role": "assistant", "content": [{"text": "\n".join(lines)}]}}


MAX_TURNS = 5

def run_agent(user_text, llm=fake_llm, messages=None):
    if messages is None:
        messages = []
    messages.append({"role": "user", "content": [{"text": user_text}]})

    for _ in range(MAX_TURNS):
        resp = llm(messages)
        messages.append(resp["message"])

        if resp["stopReason"] != "tool_use":
            return resp["message"]["content"][0]["text"]

        results = []
        for block in resp["message"]["content"]:
            if "toolUse" in block:
                tu = block["toolUse"]
                tool = TOOLS.get(tu["name"])
                if tool is None:
                    output = {"error": f"Unknown tool: {tu['name']}"}
                else:
                    try:
                        output = tool(**tu["input"])
                    except Exception as e:
                        output = {"error": str(e)}
                results.append({"toolResult": {
                    "toolUseId": tu["toolUseId"],
                    "content": [{"json": output}],
                }})
        messages.append({"role": "user", "content": results})

    return "Sorry, I couldn't finish that request."

if __name__ == "__main__":
    print(run_agent("What is the weather in Mumbai?"))
    print(run_agent("What is the weather in asdfgh?"))
    import boto3

