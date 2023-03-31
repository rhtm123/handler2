import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import subprocess

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        # self.room_group_name = 'test'

        # async_to_sync(self.channel_layer.group_add)(
        #     self.room_group_name,
        #     self.channel_name
        # )
        self.accept()
   

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        task = text_data_json.get("task") # save_code, #create_container
        code = text_data_json.get('code')
        container_name = text_data_json.get('container_name')
        file_name = text_data_json.get("file_name")
        image_name = text_data_json.get("image_name")
        # print(code, container_name, file_name)
        self.username = container_name
        # event = {"message":code, "type":"chat"};
        # self.send_msg(event)
        if task=="create_container":
            with open("tmp/output.txt", "w") as output:
                subprocess.run(f"sudo docker run -d --name {container_name} --expose 80 --net nginx-proxy -e VIRTUAL_HOST={container_name}.thelearningsetu.com {image_name}", shell=True, stdout=output, stderr=output)
            
            self.send_msg({"type":"info", "message":"container_created"})

        elif task=="save_code":
            with open("code/main.py", "w") as f:
                f.write(code)

            with open("tmp/output.txt", "w") as output:
                subprocess.run(f"sudo docker cp code/main.py {container_name}:{file_name}", shell=True, stdout=output, stderr=output)
            
            self.send_msg({"type":"info", "message":"code_saved"})

    def disconnect(self, close_code):
        try:
            with open("tmp/output.txt", "w") as output:
                subprocess.run(f"sudo docker kill {self.username};sudo docker rm -f {self.username}", shell=True, stdout=output, stderr=output)
        except:
            pass
        # print(self.username)
        self.close()

    def send_msg(self, event):
        # msg_type = event.get('type')
        # message = event.get('message')

        self.send(text_data=json.dumps(event))
    