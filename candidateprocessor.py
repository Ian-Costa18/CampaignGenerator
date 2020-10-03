import os
import smtplib
import ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from shutil import rmtree
from zipfile import ZipFile
from PIL import Image, ImageDraw, ImageFont

from imgur_downloader import ImgurDownloader

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

    font = ImageFont.truetype("Assets/font.ttf", 250)
    font_name = ImageFont.truetype("Assets/font.ttf", 300)
    draw = ImageDraw.Draw(sign)
    text = f"{position}\nOf\n{district}"
    name_w, name_h = draw.textsize(text, font=font_name)
    text_w, text_h = draw.multiline_textsize(text, font=font, spacing=20)
    draw.text(((2401 - name_w) / 2 + 253, 1400), name, (0, 0, 0), font=font_name, align="center")
    draw.multiline_text(((2401 - text_w) / 2 + 253, 1750), text, (0, 0, 0), font=font, align="center", spacing=20)

    sign.save(output, quality=95)


def send_email(receiver_email, filename):
    subject = "Your AI Generated Campaign"
    body = "Thank you for using the Campaign Generator! Submit another campaign here: https://forms.gle/iTE4DXoEEpYytyru8"
    sender_email = "campaigngeneratorjwu@gmail.com"

    with open("G:\Files\Programs\CampaignGenerator\mailcreds.txt", "r") as file:
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

    for current_candidate in candidate_list:
        # Create the campaign sign
        # Get the candidate's image from Imgur
        ImgurDownloader(current_candidate["image"]).save_images("candidate_images")  # Download Imgur image/album
        candidate_image = f"candidate_images/{os.listdir('candidate_images')[0]}"  # Find the first image in the album

        generate_sign(current_candidate["name"], current_candidate["position"], current_candidate["district"],
                      current_candidate["party"], candidate_image,
                      f"output/{current_candidate['name']} sign.png")  # Generate the sign with the candidates data
        rmtree("candidate_images")  # Delete the images folder

        # Create the campaign speech
        speech = f"""My Fellow Americans,

I stand before you today not to spew fancy political rhetoric or to talk about what could be better. I’m here today because you all are here. And you’re clearly fed up with politics. I’m here because our democracy isn’t working for all of us. You all know that this is the most important election of our lifetime. So I’m going to do something. This is why I, {current_candidate['name']}, am running to be the {current_candidate['position']} of {current_candidate['district']}.

You may think more divides us than unites us in this new era of politics. But I know we can all unite behind {current_candidate['issues'][0]}. Not only do our lives depend on making progress on {current_candidate['issues'][0]}, but so do the lives of our children.

However, putting our all towards {current_candidate['issues'][0]} won’t be enough to save our democracy. I know each and every single one you is struggling. That’s why I am also going to also focus on {current_candidate['issues'][1]} and {current_candidate['issues'][2]}. The elites in power feel too comfortable, so we need to shake things up. I am here today to listen to you, the American people, because I know you have been silenced for far too long. 

Vote {current_candidate['name']} for {current_candidate['position']} of {current_candidate['district']}!
"""
        # Write the speech to a file
        with open(f"output/{current_candidate['name']} speech.txt", "w") as file:
            file.write(speech)

        # TODO: Create campaign video

        # Zip all files in output folder
        file_paths = os.listdir("output")
        with ZipFile('output/output.zip', 'w') as zip:
            # writing each file one by one
            os.chdir("output")
            for file in file_paths:
                if "zip" not in file:
                    zip.write(file)
                    os.remove(file)
            zip.close()
            if send_to_email:
                send_email(current_candidate["email"], "output.zip")
            if os.path.exists(f"{current_candidate['name']}.zip"):
                os.remove(f"{current_candidate['name']}.zip")
            os.rename("output.zip", f"{current_candidate['name']}.zip")
            os.chdir("..")