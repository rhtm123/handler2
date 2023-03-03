from django.shortcuts import render, HttpResponse
import subprocess
from django.http import JsonResponse


import string
import random


def save_code(request):
    if request.method == "POST":
        request_data = request.POST
        code = request_data['code']
        # print(code);
        container_name = request_data['container_name'].strip();
        file_name = request_data['file_name'].strip();

        with open("code/main.py", "w") as f:
            f.write(code)

        with open("tmp/output.txt", "w") as output:
            subprocess.run(f"sudo docker cp code/main.py {container_name}:{file_name}", shell=True, stdout=output, stderr=output)

        with open("tmp/output.txt", "r") as file:
            val = file.read()
        # val = "fdafad"
        d = {"success":True, "container_name":container_name, "response":val}
        return JsonResponse(d)




def create_new_container(request):
    request_data = request.GET
    image_name = request_data['image_name']
    container_name = ''.join(random.choices(string.ascii_lowercase, k=8))

    if image_name=="hello-world":
        with open("tmp/output.txt", "w") as output:
            subprocess.run(f"sudo docker run --name {container_name} hello-world", shell=True, stdout=output, stderr=output)
    else: 
        with open("tmp/output.txt", "w") as output:
            subprocess.run(f"sudo docker run -d --name {container_name} --expose 80 --net nginx-proxy -e VIRTUAL_HOST={container_name}.thelearningsetu.com {image_name}", shell=True, stdout=output, stderr=output) 
    with open("tmp/output.txt", "r") as file:
        val = file.read()
    # val = "fdfa"
    d = {"success":True,'container_name':container_name, "response":val}

    return JsonResponse(d)


def delete_container(request):
    request_data = request.GET
    container_name = request_data['container_name'].strip();
    with open("tmp/output.txt", "w") as output:
        subprocess.run(f"sudo docker kill {container_name};sudo docker rm -f {container_name}", shell=True, stdout=output, stderr=output)

    with open("tmp/output.txt", "r") as file:
        val = file.read()
    d = {"success":True, "container_name":container_name, "response":val}
    return JsonResponse(d)


def show_containers(request):
    with open("tmp/output.txt", "w") as output:
        subprocess.run(f"sudo docker container ls -a", shell=True, stdout=output, stderr=output)

    with open("tmp/output.txt", "r") as file:
        val = file.read()
    d = {"success":True,"containers":val}

    return JsonResponse(d)
