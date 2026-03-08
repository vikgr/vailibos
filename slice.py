import sys
from PIL import Image

def slice_it():
    try:
        img = Image.open('/tmp/covers.png')
        img = img.convert('RGB')
        
        c1 = img.crop((60, 170, 335, 570))
        c2 = img.crop((365, 170, 660, 570))
        c3 = img.crop((695, 170, 970, 570))
        
        c1.save('/tmp/cover0.jpg', 'JPEG')
        c2.save('/tmp/cover1.jpg', 'JPEG')
        c3.save('/tmp/cover2.jpg', 'JPEG')
        print("Success")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    slice_it()
