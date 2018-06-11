from PIL import Image,ImageFilter,ImageFont,ImageDraw,ImageColor
import os
from app.config import COMPOSITE_IMAGE_FOLDER,FONT_STYLE_FOLDER,UPLOAD_FOLDER


def compositeImage(image_name,actions):
    image_path = os.path.join(UPLOAD_FOLDER,image_name)
    outfile = os.path.join(COMPOSITE_IMAGE_FOLDER,image_name)

    with Image.open(image_path).convert('RGBA') as im:
        print(im.size)
        img = im.copy()
        for action in actions:
            if action['action'] == 'text':
                img = _addText(
                    img,
                    action['text'],
                    position=tuple(action['position']),
                    font_size=action['font-size']
                )
            elif action['action'] == 'line':
                img = _addLine(
                    img,
                    position = tuple(action['position']),
                    width = action['width']
                )
        img.save(outfile, "PNG")
    return True


def _addText(im,text,position=(0,0),font_style='6',font_size=20,color=(0,0,0),opacity=255):

        blank = Image.new('RGBA', im.size, (255,255,255,0))
        txtLayer = ImageDraw.Draw(blank)
        if str(font_size).endswith('px'):
            # font_size = str(font_size)[0:-2]
            font_size = int(float(str(font_size)[0:-2]))
        fnt = ImageFont.truetype(os.path.join(FONT_STYLE_FOLDER,'{}.otf'.format(str(font_style))), int(font_size))
        txtLayer.text(position, text, font=fnt, fill=color+(opacity,))

        return Image.alpha_composite(im, blank)

def _addLine(im,position=(0,0,0,0),width=1,color=(255,255,255),opacity=255):
    # PIL.ImageDraw.ImageDraw.line(xy, fill=None, width=0)
        draw = ImageDraw.Draw(im)
        draw.line(position,fill=color + (opacity,),width=width)
        del draw
        return im
