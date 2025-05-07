# MIT License
# Copyright (c) 2025 JinxedUp
import json
import asyncio
import httpx
from httpx_ws import aconnect_ws

class GatewayClient:
    def __init__(self, token, handler):
        self.token = token
        self.handler = handler
        self.ws_url = "wss://gateway.discord.gg/?v=9&encoding=json"

    async def connect(self):
        print("Connecting to Discord Gateway...")
        while True:
            try:

                async with aconnect_ws(self.ws_url) as ws:
                    print("Connected to Gateway, waiting for HELLO...")
                    hello = await ws.receive_json()  
                    interval = hello["d"]["heartbeat_interval"] / 1000  
                    print(f"Received HELLO, heartbeat interval: {interval}s")

                    identify_payload = {
                        "op": 2,
                        "d": {
                            "token": self.token,
                            "intents": 32767,  
                            "properties": {
                                "$os": "windows",
                                "$browser": "chrome",
                                "$device": "desktop"
                            }
                        }
                    }

                    print("Sending identify payload...")
                    await ws.send_json(identify_payload)

                    async def heartbeat():
                        while True:
                            await asyncio.sleep(interval)
                            await ws.send_json({"op": 1, "d": None})

                    asyncio.create_task(heartbeat())
                    print("Heartbeat task started")

                    while True:
                        try:
                            msg = await ws.receive_json()
                            print(f"Received gateway message: {msg}")  

                            if isinstance(msg, dict) and "op" in msg:
                                if msg["op"] == 0:  
                                    event_type = msg.get("t")
                                    event_data = msg.get("d", {})
                                    print(f"Processing event: {event_type}")

                                    if event_type == "READY":
                                        print("Received READY event")

                                        self.handler.user_id = event_data["user"]["id"]
                                        print(f"Bot user ID set to: {self.handler.user_id}")

                                    event_data["_event_type"] = event_type
                                    await self.handler.handle(event_data)
                                elif msg["op"] == 10:  
                                    print("Received HELLO event")
                                elif msg["op"] == 11:  
                                    print("Received heartbeat ACK")
                        except Exception as e:
                            print(f"Error processing message: {e}")
                            continue

            except Exception as e:
                print(f"Gateway error: {e}. Reconnecting in 5 seconds...")
                await asyncio.sleep(5)
