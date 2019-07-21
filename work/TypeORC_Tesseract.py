import pytesseract
from PIL import Image
import cv2

pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract.exe'
image_sour = "D:/Users/84460/Desktop/Oracle_Split/Picture/01/0001.png"
text = pytesseract.image_to_string(image_sour, lang = "chi_sim_vert")

print(text)