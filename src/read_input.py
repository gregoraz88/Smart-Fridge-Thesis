import cv2
from pyzbar import pyzbar
import argparse
import imutils
import json
from os import getcwd,path
from fridge_manager import check_and_return_barcode_existance,fridge_contet
import time

def read_barcode(fridge_obj):
    cap = cv2.VideoCapture(1)
    while (True):
        ret,frame = cap.read()
        frame = imutils.resize(frame,width=400)
        detected_barcodes = pyzbar.decode(frame)
        for barcode in detected_barcodes:
            (x,y,w,h)= barcode.rect
            cv2.rectangle = (frame,(x,y), (x+w, y+h), (255,0,0),5)
            print('--------------------------------------')
            check_and_return_barcode_existance(str(barcode.data),fridge_obj)
            time.sleep(3)
        cv2.imshow('preview',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

def init_fridge():
    fridge_obj = fridge_contet('Greg')
    return fridge_obj

def main():
    fridge_object = init_fridge()
    read_barcode(fridge_object)
main()
