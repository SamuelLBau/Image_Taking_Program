import Tkinter as tk
import tkFileDialog
import cv2
import threading,time
from glob import glob
import os


from copy import deepcopy

class main_app(tk.Frame):
    
    OPTION_LIST = ["NO_stringiness","LOW_stringiness","MED_stringiness","HIGH_stringiness"]
    DEFAULT_DATA_DIR = "./example_data/"
    DEFAULT_CROP_SIZE = [100,100] #Height, width
    BOX_COLOR = (0,0,255)
    
    def __init__(self,master):
        tk.Frame.__init__(self,master)
        cv2.namedWindow("preview")
        self.create_widgets()
        self.save_image_flag = False
        self.crop_size = self.DEFAULT_CROP_SIZE
        
        self.thread = threading.Thread(target=self.update_image)
        self.thread.start()
        
    def create_widgets(self):
        
        self.ctr_FRAME = tk.Frame(self)
        
        #Add control objects to control frame
        self.path_SV    = tk.StringVar()
        self.path_SV.set(self.DEFAULT_DATA_DIR)
        self.path_LABEL = tk.Label(self.ctr_FRAME,text="Image Directory:")
        self.path_ENTRY = tk.Entry(self.ctr_FRAME,textvariable=self.path_SV)
        self.path_BUTTON= tk.Button(self.ctr_FRAME,text="...",command=self.prompt_new_path)
        
        self.active_quality_SV = tk.StringVar(self)
        self.active_quality_SV.set(self.OPTION_LIST[0])
        self.quality_dropdown = tk.OptionMenu(self.ctr_FRAME,self.active_quality_SV,*self.OPTION_LIST)
        
        self.image_save_width_SV = tk.StringVar(self)
        self.image_save_width_SV.set(self.DEFAULT_CROP_SIZE[1])
        self.image_save_width_LABEL = tk.Label(self,text="Width")
        self.image_save_width_ENTRY = tk.Entry(self,textvariable=self.image_save_width_SV)
        
        self.image_save_height_SV = tk.StringVar(self)
        self.image_save_height_SV.set(self.DEFAULT_CROP_SIZE[1])
        self.image_save_height_LABEL = tk.Label(self,text="Height")
        self.image_save_height_ENTRY = tk.Entry(self,textvariable=self.image_save_height_SV)
        
        self.take_image_BUTTON = tk.Button(self.ctr_FRAME,text="Take Image",command=self.save_image)
        
        self.path_LABEL.grid(row=0,column=0)
        self.path_ENTRY.grid(row=0,column=1)
        self.path_BUTTON.grid(row=0,column=2)
        
        self.quality_dropdown.grid(row=1,column=0,columnspan=3)
        
        self.image_save_width_LABEL.grid(row=2,column=0)
        self.image_save_width_ENTRY.grid(row=2,column=1,columnspan=2)
        self.image_save_height_LABEL.grid(row=3,column=0)
        self.image_save_height_ENTRY.grid(row=3,column=1,columnspan=2)
        
        self.take_image_BUTTON.grid(row=4,column=0,columnspan=3)
        
        
        #Places items on top frame
        self.ctr_FRAME.grid()
        self.pack()
    def save_image(self,event=None):
        image_dir = self.path_SV.get() + "/" + self.active_quality_SV.get() + "/"
        if not os.path.isdir(image_dir):
            os.mkdir(image_dir)
        print(image_dir)
        file_list = glob(image_dir + "Image*.png")
        cur_num = 0
        for file in file_list:
            str_list = file.split("_")
            final_bit = str_list[-1].replace(".png","")
            num = int(final_bit)
            if not num == cur_num:
                break
            cur_num += 1
        image_name = str("Image_%d.png"%(cur_num))
        self.image_path = image_dir + image_name
        self.image_path = self.image_path.replace("\\","/")
        self.save_image_flag = True
        
        #NOTE: IMAGE IS SAVED BY THE THREADED FUNC "UPDATE IMAGE"
        
    
    
    def prompt_new_path(self,event=None):
        folder_dir = tkFileDialog.askdirectory()
        self.path_SV.set(folder_dir)
        
    def update_image(self=None):
        vc = cv2.VideoCapture(0)
        if vc.isOpened(): # try to get the first frame
            rval, frame = vc.read()
        else:
            rval = False
        if rval:
            width  = frame.shape[0]
            height   = frame.shape[1]
            
            box_frame = deepcopy(frame)
            try:
                crop_size = [int(self.image_save_width_SV.get()),int(self.image_save_height_SV.get())]
                unused_height = height - crop_size[0]
                unused_width = width - crop_size[1]
                
                tl_point = (int(unused_height/2),int(unused_width/2))
                br_point = (tl_point[0]+crop_size[0],tl_point[1]+crop_size[1])
                
                box_frame = deepcopy(frame)
                cv2.rectangle(box_frame,tl_point,br_point,self.BOX_COLOR,thickness=3)
            except:
                print("Could not draw rectangle, width / height not valid")
            cv2.imshow("preview", box_frame)
            
            if self.save_image_flag:
                cropped_image = frame[tl_point[1]:br_point[1],tl_point[0]:br_point[0]]
                print("SAVING CURRENT IMAGE TO %s"%(self.image_path))
                cv2.imwrite(self.image_path,cropped_image)
                self.save_image_flag = False
            
        self.thread = threading.Thread(target=self.update_image, args=())
        self.thread.start()