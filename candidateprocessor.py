""" Main functionality """

import os
import smtplib
import ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from shutil import rmtree
from zipfile import ZipFile

import cv2
from PIL import Image, ImageDraw, ImageFont
from imgur_downloader import ImgurDownloader
from moviepy.editor import VideoFileClip, concatenate_videoclips

CWD = os.getcwd()+"/"

def generate_sign(name, position, district, party, image, output):
    sign_templates = {
        "democrat": "Assets/Demsign.png",
        "republican": "Assets/Repsign.png",
        "independant": "Assets/Indsign.png"
    }
    template = Image.open(sign_templates[party.lower()])
    img = Image.open(image)
    sign = template.copy()
    img = img.resize((2197, 3304))
    sign.paste(img, (2906, 0))

    font = ImageFont.truetype(CWD+"Assets/font.ttf", 250)
    font_name = ImageFont.truetype(CWD+"Assets/font.ttf", 300)
    draw = ImageDraw.Draw(sign)
    text = f"{position}\nOf\n{district}"
    name_w, name_h = draw.textsize(text, font=font_name)
    text_w, text_h = draw.multiline_textsize(text, font=font, spacing=20)
    draw.text(((2401 - name_w) / 2 + 253, 1400), name, (0, 0, 0), font=font_name, align="center")
    draw.multiline_text(((2401 - text_w) / 2 + 253, 1750), text, (0, 0, 0),
                        font=font, align="center", spacing=20)

    sign.save(output, quality=95)

def generate_video(sign, issue, output):
    """ Generates a campaign video based on the issue
    output variable determines where the file will be saved"""

    videos = {
        "Climate Change": "ClimateChange.mp4",
        "Green Jobs": "GreenJobs.mp4",
        "Tourism": "Tourism.mp4",
        "Small Business": "SmallBusiness.mp4",
        "Public health": "PublicHealth.mp4",
        "Education Funding": "EducationFunding.mp4"
    }

    video_path = CWD+f"Assets/{videos[issue]}"

    frame = cv2.imread(sign)
    frame = cv2.resize(frame, (1920, 1080))
    height, width, layers = frame.shape
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(CWD+"temp.mp4", fourcc, 1, (width, height))
    for i in range(5):
        video.write(frame)
    video.release()

    image_clip = VideoFileClip(CWD+"temp.mp4")
    original_video = VideoFileClip(video_path)
    final_video = concatenate_videoclips([original_video, image_clip], method="compose")

    final_video.write_videofile(output)
    os.remove(CWD+"temp.mp4")


def send_email(receiver_email, filename):
    """ Sends an email with an attachment """

    subject = "Your AI Generated Campaign"
    body = "Thank you for using the Campaign Generator! Submit another campaign here: https://forms.gle/iTE4DXoEEpYytyru8"
    sender_email = "campaigngeneratorjwu@gmail.com"

    with open(CWD+"mailcreds.txt", "r") as file:
        password = file.read()

    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message["Bcc"] = receiver_email  # Recommended for mass emails

    # Add body to email
    message.attach(MIMEText(body, "plain"))

    # Open PDF file in binary mode
    with open(filename, "rb") as attachment:
        # Add file as application/octet-stream
        # Email client can usually download this automatically as attachment
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    # Encode file in ASCII characters to send by email
    encoders.encode_base64(part)

    # Add header as key/value pair to attachment part
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename}",
    )

    # Add attachment to message and convert message to string
    message.attach(part)
    text = message.as_string()

    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)


def process_candidate(candidate_list, send_to_email=True):
    """ Main function that generates the sign, video, and speech using the helper functions,
     then sends the campaign in a zip over email
      set send_to_email to false to disable emailing functionality"""

    for current_candidate in candidate_list:
        # Create the campaign sign
        # Get the candidate's image from Imgur
        ImgurDownloader(current_candidate["image"]).save_images(CWD+"candidate_images")  # Download Imgur image/album
        candidate_image = CWD+f"candidate_images/{os.listdir('candidate_images')[0]}"  # Find the first image in the album

        # Generate the sign with the candidates data
        sign_output = CWD+f"output/{current_candidate['name']} sign.png"
        generate_sign(current_candidate["name"], current_candidate["position"],
                      current_candidate["district"], current_candidate["party"],
                      candidate_image, sign_output)
        rmtree(CWD+"candidate_images")  # Delete the images folder

        # Create the campaign speech
        speech = f"""My Fellow Americans,

I stand before you today not to spew fancy political rhetoric or to talk about what could be better. I’m here today because you all are here. And you’re clearly fed up with politics. I’m here because our democracy isn’t working for all of us. You all know that this is the most important election of our lifetime. So I’m going to do something. This is why I, {current_candidate['name']}, am running to be the {current_candidate['position']} of {current_candidate['district']}.

You may think more divides us than unites us in this new era of politics. But I know we can all unite behind {current_candidate['issues'][0]}. Not only do our lives depend on making progress on {current_candidate['issues'][0]}, but so do the lives of our children.

However, putting our all towards {current_candidate['issues'][0]} won’t be enough to save our democracy. I know each and every single one you is struggling. That’s why I am also going to also focus on {current_candidate['issues'][1]} and {current_candidate['issues'][2]}. The elites in power feel too comfortable, so we need to shake things up. I am here today to listen to you, the American people, because I know you have been silenced for far too long. 

Vote {current_candidate['name']} for {current_candidate['position']} of {current_candidate['district']}!
"""
        # Write the speech to a file
        with open(CWD+f"output/{current_candidate['name']} speech.txt", "w") as file:
            file.write(speech)

        generate_video(sign_output, current_candidate["issues"][0],
                       CWD+f"output/{current_candidate['name']} video.mp4")

        # Zip all files in output folder
        file_paths = os.listdir(CWD+"output")
        with ZipFile(CWD+'output\\Generated Campaign.zip', 'w') as zipped:
            # writing each file one by one
            os.chdir(CWD+"\\output")
            for file in file_paths:
                if "zip" not in file:
                    zipped.write(file, arcname=file)
                    os.remove(file)
            zipped.close()
            if send_to_email:
                send_email(current_candidate["email"], "Generated Campaign.zip")
            if os.path.exists(f"{current_candidate['name']}.zip"):
                os.remove(f"{current_candidate['name']}.zip")
            os.rename("Generated Campaign.zip", f"{current_candidate['name']}.zip")
            os.chdir("..")

