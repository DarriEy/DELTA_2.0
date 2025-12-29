# backend/setup_credentials.py
import base64
import os

def setup():
    input_file = "credentials-base64.txt"
    output_file = "google-credentials.json"
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    with open(input_file, "r") as f:
        base64_str = f.read().strip()
    
    try:
        # Some base64 files might have headers or be wrapped, 
        # but let's assume it's a clean base64 string.
        decoded_bytes = base64.b64decode(base64_str)
        with open(output_file, "wb") as f:
            f.write(decoded_bytes)
        print(f"Successfully decoded and saved to {output_file}")
    except Exception as e:
        print(f"Error decoding credentials: {e}")

if __name__ == "__main__":
    setup()
