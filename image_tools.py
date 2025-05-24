from PIL import Image

def resize_image(path, output_path, size=(512, 512)):
    """
    Змінює розмір зображення і зберігає за новим шляхом.
    """
    img = Image.open(path)
    img = img.convert("RGB")
    img = img.resize(size)
    img.save(output_path)
    return output_path

def image_to_bytes(path):
    """
    Зчитує зображення і повертає його як bytes.
    """
    with open(path, "rb") as f:
        return f.read()