import requests

api_key = "sk_3ce4f1ccb97fa8fd0a27bf19c2ac222e135834da"
url = "https://api.pdfshift.io/v3/convert/pdf"

response = requests.post(
    url,
    auth=(api_key, ''),
    json={"source": "<html><body><h1>Test PDF</h1></body></html>"}
)

print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    print("PDF generated successfully!")
else:
    print(f"Error: {response.text}")