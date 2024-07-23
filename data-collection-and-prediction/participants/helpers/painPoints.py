
from PIL import Image, ImageDraw, ImageFont
import os
from django.conf import settings

def renderPainPointsOfParticipant(participant_instance):
    image_path = "./participants/static/feet-new.jpg"
    
    font = ImageFont.load_default()


    # Open the image
    img = Image.open(image_path)

    # Create a drawing object
    draw = ImageDraw.Draw(img)
    
    markings = []
    
    try:
        markings = participant_instance.pain_points['markings']            
    except:
        print("could not load markings")
        return
        pass

    # Draw circles on the image
    for marking in markings:
        x, y = float(marking['x']), float(marking['y'])
        draw.ellipse((x, y , x + 20, y+20), fill=(255, 0, 0))
        
        if 'pain' in marking:
            draw.text((x+5,y+5), marking['pain'], font=font, fill="black")

    # Save the modified image
    destination_folder = os.path.join(settings.MEDIA_ROOT, "pain_points")
        
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
        
        
    filename_png = os.path.join(destination_folder, "pain_points-"+ str(participant_instance.id)+".png")
    participant_instance.pain_points_render.name = os.path.relpath(filename_png, settings.MEDIA_ROOT)
    #self.save()
    img.save(filename_png)

    print(f"Image with circles saved at: {filename_png}")