import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import subprocess

import socket

DOMAIN_NAME = "nikhilmohite.info"

def find_available_port(start_port, end_port):
    for port in range(start_port, end_port + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("0.0.0.0", port))
                return port
            except OSError:
                pass
    return None


def run_docker_container(container_name, image_name):
    host_port = find_available_port(3000, 3100)
    command = f"sudo docker run -d -p {host_port}:80 --name {container_name} {image_name}"
    subprocess.run(command, shell=True, check=True)
  
def create_nginx_config(container_name, subdomain):
    # Create an Nginx configuration file for the container
    nginx_config = f"""
    server {{
        listen 80;
        server_name {subdomain};

        location / {{
            proxy_pass http://{container_name}:80; # Assuming your app runs on port 80 in the Docker container
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }}
    }}
    """

    # Write the configuration to a file
    config_file_path = f"/etc/nginx/sites-available/{container_name}"
    with open(config_file_path, "w") as config_file:
        config_file.write(nginx_config)

    # Create a symbolic link to enable the Nginx configuration
    enable_command = f"sudo ln -s {config_file_path} /etc/nginx/sites-enabled/"
    subprocess.run(enable_command, shell=True, check=True)

def delete_nginx_config(container_name):
    # Remove the symbolic link to disable the Nginx configuration
    disable_command = f"sudo rm /etc/nginx/sites-enabled/{container_name}"
    subprocess.run(disable_command, shell=True, check=True)

    # Delete the configuration file
    config_file_path = f"/etc/nginx/sites-available/{container_name}"
    subprocess.run(f"sudo rm {config_file_path}", shell=True, check=True)

def reload_nginx():
    # Test Nginx configuration and reload if it's valid
    subprocess.run("sudo nginx -t", shell=True, check=True)
    subprocess.run("sudo systemctl reload nginx", shell=True, check=True)
    

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
                run_docker_container(container_name)
                subdomain = container_name + "." + DOMAIN_NAME
                create_nginx_config(container_name, subdomain)
                reload_nginx()
                
                
                # subprocess.run(f"sudo docker run -d --name {container_name} --expose 80 --net nginx-proxy -e VIRTUAL_HOST={container_name}.thelearningsetu.com {image_name}", shell=True, stdout=output, stderr=output)
            
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
                delete_nginx_config(sekf.username)
                reload_nginx()
                # subprocess.run(f"sudo docker kill {self.username};sudo docker rm -f {self.username}", shell=True, stdout=output, stderr=output)
        except:
            pass
        # print(self.username)
        # self.close()

    def send_msg(self, event):
        # = event.get('type')
        # message = event.get('message')

        self.send(text_data=json.dumps(event))
    
