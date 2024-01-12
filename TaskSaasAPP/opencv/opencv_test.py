import cv2
import pytesseract

# 并不好用
pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'

# img = cv2.imread('/Users/tanghuijuan/PycharmProjects/TaskSaas/web/static/uploads/2024011208140036389812023-12-09 16.05.01.png')
img = cv2.imread('/Users/tanghuijuan/Desktop/cv2test1.png')

gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
_, thresh = cv2.threshold(gray,0,255,cv2.THRESH_BINARY + cv2.THRESH_OTSU)

# text = pytesseract.image_to_string(thresh,lang='eng') #可以设置语言参数
text = pytesseract.image_to_string(thresh,lang='Hans') #可以设置语言参数

print(text)