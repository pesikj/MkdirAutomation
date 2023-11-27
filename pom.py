import subprocess

result = subprocess.run("sestatus", stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
print(result.stderr)