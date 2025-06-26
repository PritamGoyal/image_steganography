from PIL import Image
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random
import base64

DEBUG = False
headerText = "M6nMjy5THr2J"
SUPPORTED_FORMATS = ['PNG', 'JPEG', 'JPG', 'TIFF', 'BMP', 'JFIF', 'WEBP']


def encrypt(key, source, encode=True):
    key = SHA256.new(key).digest()
    IV = Random.new().read(AES.block_size)
    encryptor = AES.new(key, AES.MODE_CBC, IV)
    padding = AES.block_size - len(source) % AES.block_size
    source += bytes([padding]) * padding
    data = IV + encryptor.encrypt(source)
    return base64.b64encode(data).decode() if encode else data


def decrypt(key, source, decode=True):
    if decode:
        source = base64.b64decode(source.encode())
    key = SHA256.new(key).digest()
    IV = source[:AES.block_size]
    decryptor = AES.new(key, AES.MODE_CBC, IV)
    data = decryptor.decrypt(source[AES.block_size:])
    padding = data[-1]
    if data[-padding:] != bytes([padding]) * padding:
        raise ValueError("Invalid padding.")
    return data[:-padding]


def convertToRGB(img):
    if img.mode == 'RGB':
        return img
    rgba_image = img.convert('RGBA')
    background = Image.new("RGB", rgba_image.size, (255, 255, 255))
    background.paste(rgba_image)
    return background


def calculate_required_dimensions(message_length, max_pixels_per_character=3 * 8):
    pixels_needed = message_length * max_pixels_per_character
    width = int((pixels_needed ** 0.5) + 0.5)
    height = (pixels_needed + width - 1) // width
    return width, height


def encodeImage(image, message, filename="temp.png"):
    width, height = image.size
    pix = image.getdata()

    current_pixel = 0
    tmp = 0
    x = 0
    y = 0

    for ch in message:
        binary_value = format(ord(ch), '08b')
        p1 = pix[current_pixel]
        p2 = pix[current_pixel + 1]
        p3 = pix[current_pixel + 2]
        three_pixels = [val for val in p1 + p2 + p3]

        for i in range(8):
            current_bit = binary_value[i]
            if current_bit == '0':
                if three_pixels[i] % 2 != 0:
                    three_pixels[i] = three_pixels[i] - 1 if three_pixels[i] == 255 else three_pixels[i] + 1
            elif current_bit == '1':
                if three_pixels[i] % 2 == 0:
                    three_pixels[i] = three_pixels[i] - 1 if three_pixels[i] == 255 else three_pixels[i] + 1

        current_pixel += 3
        tmp += 1

        if tmp == len(message):
            if three_pixels[-1] % 2 == 0:
                three_pixels[-1] = three_pixels[-1] - 1 if three_pixels[-1] == 255 else three_pixels[-1] + 1
        else:
            if three_pixels[-1] % 2 != 0:
                three_pixels[-1] = three_pixels[-1] - 1 if three_pixels[-1] == 255 else three_pixels[-1] + 1

        three_pixels = tuple(three_pixels)
        st = 0
        end = 3

        for i in range(3):
            image.putpixel((x, y), three_pixels[st:end])
            st += 3
            end += 3
            if x == width - 1:
                x = 0
                y += 1
            else:
                x += 1

    image.save(filename)
    return filename


def decodeImage(image):
    pix = image.getdata()
    current_pixel = 0
    decoded = ""

    while True:
        binary_value = ""
        try:
            p1 = pix[current_pixel]
            p2 = pix[current_pixel + 1]
            p3 = pix[current_pixel + 2]
        except IndexError:
            break

        three_pixels = [val for val in p1 + p2 + p3]

        for i in range(8):
            binary_value += "0" if three_pixels[i] % 2 == 0 else "1"

        ascii_value = int(binary_value, 2)
        decoded += chr(ascii_value)
        current_pixel += 3

        if three_pixels[-1] % 2 != 0:
            break

    return decoded
