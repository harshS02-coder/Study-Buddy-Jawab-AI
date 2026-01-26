import cloudinary
import cloudinary.uploader
import os
from dotenv import load_dotenv

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)

def upload_file(file, folder):
    result = cloudinary.uploader.upload(
        file,
        resource_type="raw",
        folder=folder
    )
    print(f"File uploaded to Cloudinary: {result.get('secure_url')}")
    return result["secure_url"]
