import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import subprocess

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_group_name = 'test'

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()
   

    def receive(self, text_data):
        # print(text_data['container'])
        text_data_json = json.loads(text_data)
        # print(text_data_json)
        code = text_data_json.get('code')
        container_name = text_data_json.get('container_name')
        file_name = text_data_json.get("file_name")
        print(code, container_name, file_name)
        if code:
            with open("code/main.py", "w") as f:
                f.write(code)

                with open("tmp/output.txt", "w") as output:
                    subprocess.run(f"sudo docker cp code/main.py {container_name}:{file_name}", shell=True, stdout=output, stderr=output)

                # with open("tmp/output.txt", "r") as file:
                #     val = file.read()
                # val = "fdafad"
                # d = {"success":True, "container_name":container_name, "response":val}
                
        # async_to_sync(self.channel_layer.group_send)(
        #     self.room_group_name,
        #     {
        #         'type':'chat_message',
        #         'message':message
        #     }
        # )

    def chat_message(self, event):
        message = event['message']

        self.send(text_data=json.dumps({
            'type':'chat',
            'message':message
        }))