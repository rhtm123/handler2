import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import subprocess
from django.core.management import call_command


import socket
import docker
import sys
import shutil
import os



DOMAIN_NAME = "nikhilmohite.info"
host_port = ""

def find_available_port(start_port, end_port):
    for port in range(start_port, end_port + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("0.0.0.0", port))
                return port
            except OSError:
                pass
    return None


def run_process(cmd, filename):
    with open(filename, "w") as output:
        print("command- ", cmd, "filename - ", filename)
        subprocess.run(cmd, shell=False, stdout=output, stderr=output)

def run_docker_container(container_name, image_name):
    global host_port
    host_port = find_available_port(3000, 3100)
    print("host port found", host_port)

    client = docker.from_env()

    # Define the container configuration
    container_config = {
        "image": image_name,       # Specify the Docker image to run
        "name": container_name,    # Specify the container name
        "detach": True,            # Run the container in the background
        "ports": {"80/tcp": host_port} # Map container port 80 to host port 8080
    }
    # Run the Docker container
    container = client.containers.run(**container_config)

    # Print the container ID
    print(f"Container ID for '{container_name}': {container.id}")

    
    #command = f"docker run -d -p {host_port}:80 --name {container_name} --expose 80 {image_name}"
    # run_process(command, "tmp/outcome6.txt")
    #print("Container Created")
    # subprocess.run(command, shell=True, check=True)
  
def create_nginx_config(container_name, subdomain):
    # Create an Nginx configuration file for the container
    nginx_config = f"""
    server {{
        listen 80;
        server_name {subdomain};

        location / {{
            proxy_pass http://127.0.0.1:{host_port}; # Assuming your app runs on port 80 in the Docker container
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }}

        location /pty {{
            proxy_pass http://127.0.0.1:{host_port};
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }}

    }}
    """

    # Write the configuration to a file
    temp_file = f"/home/rohit/handler2/temp/{container_name}"
    with open(temp_file, "w") as config_file:
        config_file.write(nginx_config)

    sites_available = "/etc/nginx/sites-available/" + container_name
    shutil.copy(temp_file, sites_available)

    print("Config file created")
    # Create a symbolic link to enable the Nginx configuration
    #enable_command = f"sudo ln -s {config_file_path} /etc/nginx/sites-enabled/"
    sites_enabled = "/etc/nginx/sites-enabled/"+container_name
    os.symlink(sites_available, sites_enabled)
    #run_process(f"sudo cp /home/rohit/handler2/temp/{container_name} /etc/nginx/sites-available/", "tmp/outcome7.txt")
    #run_process( enable_command, "tmp/outcome5.txt")
    print("Symbolic link created")
    # subprocess.run(enable_command, shell=True, check=True)

def delete_nginx_config(container_name):
    # Remove the symbolic link to disable the Nginx configuration
    # disable_command = f"sudo rm /etc/nginx/sites-enabled/{container_name}"
    site_enabled_file = f"/etc/nginx/sites-enabled/{container_name}"
    os.remove(site_enabled_file)

    

    #run_process(disable_command, "tmp/outcome3.txt")
    
    # Delete the configuration file
    config_file_path = f"/etc/nginx/sites-available/{container_name}"
    os.remove(config_file_path)

    temp_file = f"/home/rohit/handler2/temp/{container_name}"
    os.remove(temp_file)

    #run_process( f"sudo rm {config_file_path}" ,"tmp/outcome4.txt")
    #run_process( f"sudo rm /home/rohit/handler2/temp/{container_name}" ,"tmp/outcome4.txt")
    print("NGINX files deleted")
    # subprocess.run(f"sudo rm {config_file_path}", shell=True, check=True)

def reload_nginx():
    # Test Nginx configuration and reload if it's valid
    run_process("sudo /usr/sbin/nginx -t", "tmp/outcome1.txt")
    # subprocess.run(["nginx", "-t"])
    # call_command('nginx_reload_command')
    # subprocess.run(["nginx", "-s", "reload"])
    run_process("sudo /usr/sbin/nginx -s reload", "tmp/outcome2.txt")
    print("nginx reload successful")

def docker_running(container_name):
    client = docker.from_env()
    try:
    # Get information about the container
        container_info = client.containers.get(container_name)
    
            # Check if the container is running
        if container_info.status == "running":
            return True
        else:
            return False
    except docker.errors.NotFound:
        return False
    except docker.errors.APIError as e:
        print(f"An error occurred while checking the container: {str(e)}")
    
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

            if not docker_running(container_name):
                run_docker_container(container_name, image_name)
                subdomain = container_name + "." + DOMAIN_NAME
                create_nginx_config(container_name, subdomain)
                
                reload_nginx()
                
                
                # subprocess.run(f"sudo docker run -d --name {container_name} --expose 80 --net nginx-proxy -e VIRTUAL_HOST={container_name}.thelearningsetu.com {image_name}", shell=True, stdout=output, stderr=output)
            
            self.send_msg({"type":"info", "message":"container_created"})

        elif task=="save_code":
            with open("code/main.py", "w") as f:
                f.write(code)

            with open("tmp/output.txt", "w") as output:
                subprocess.run(f"docker cp code/main.py {container_name}:{file_name}", shell=True, stdout=output, stderr=output)
            
            self.send_msg({"type":"info", "message":"code_saved"})

    def disconnect(self, close_code):
        try:
            with open("tmp/output.txt", "w") as output:
                print("disconnected")
                delete_nginx_config(self.username)
                run_process(f"docker kill {self.username};docker rm -f {self.username}", "tmp/outcome.txt")
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
    
