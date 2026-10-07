# bedrock_llm.py
import boto3

client = boto3.client("bedrock-runtime", region_name="YOUR_REGION")
MODEL_ID = "YOUR_MODEL_ID"

SYSTEM = [{"text": "You are a weather assistant. Use the get_forecast tool for any weather question. Be brief."}]

tool_config = {
    "tools": [{
        "toolSpec": {
            "name": "get_forecast",
            "description": "Get the daily weather forecast for a city.",
            "inputSchema": {"json": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name, e.g. Mumbai"},
                    "days": {"type": "integer", "description": "Days to forecast (1-7)"},
                },
                "required": ["city"],
            }},
        }
    }]
}

def bedrock_llm(messages):
    resp = client.converse(
        modelId=MODEL_ID,
        messages=messages,
        system=SYSTEM,
        toolConfig=tool_config,
    )
    return {"stopReason": resp["stopReason"], "message": resp["output"]["message"]}