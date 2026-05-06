import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
import os

from sendEmail import send_email

load_dotenv()


cloudinary_url = os.getenv("CLOUDINARY_URL")
cloudinary.config(
    cloud_name="dd2at7bts",
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

def upload_pdf(filename):
    print('my filename in upload pdf is', filename)
    res = cloudinary.uploader.upload(f"reciepts/{filename}.pdf", resource_type="auto")
    print('we are uploading pdf',res)
    send_email(to=os.getenv("email"), subject="Your Receipt", text=f"Your receipt is available at {res['secure_url']}")
    return res['secure_url']


