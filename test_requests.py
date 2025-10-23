import requests

print("contacting an example website...")

response = requests.get("https://httpbin.org/json", timeout=5)

#Inspect the result
print("Status code:", response.status_code)
print("Headers:", response.headers["Content-type"])
print("JSON keys returned:", list(response.json().keys()))