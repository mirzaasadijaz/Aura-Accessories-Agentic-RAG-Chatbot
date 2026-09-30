import requests
import os

# Aapke backend ka upload link
url = "http://127.0.0.1:8000/upload"

# Yahan us PDF ka naam likhein jo aap upload karna chahte hain
file_name = "document.pdf" 

if not os.path.exists(file_name):
    print(f"Error: '{file_name}' folder mein mojood nahi hai. Pehle PDF yahan rakhein.")
else:
    print(f"Uploading {file_name} to server...")
    
    # File ko read kar ke API par POST request bhejna
    with open(file_name, "rb") as file:
        files = {"file": (file_name, file, "application/pdf")}
        response = requests.post(url, files=files)
        
        # Result check karna
        if response.status_code == 200:
            print("Upload Successful! 🎉")
            print("Server Response:", response.json())
        else:
            print(f"Upload Failed. Status Code: {response.status_code}")
            print("Error Details:", response.text)