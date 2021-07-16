import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import messagebox
import cv2 as cv
import numpy as np
from PIL import ImageTk, Image
import os

def displayImg(img):
  """
  Zooms and then converts cv image to tkinter image.
  """
  h, w = img.shape[:2]
  sc = min(490/h, 490/w) # scaling factor
  img = cv.resize(img, None, fx=sc, fy=sc, interpolation=cv.INTER_LINEAR)
  img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
  imgtk = ImageTk.PhotoImage(image=Image.fromarray(img))
  return imgtk

class Transformations:
  
  def __init__(self, root):
    content = ttk.Frame(root)
    imageFrame = ttk.Labelframe(content, text='Image', height=530, width=500)
    imageFrame.grid_propagate(False)
    self.imageLabel = ttk.Label(imageFrame)
    self.fileText = tk.StringVar()
    imageSize = ttk.Label(imageFrame, textvariable=self.fileText)
    transFrame = ttk.Labelframe(content, text='Transformations', height=100, width=250)
    buttonFrame = ttk.Labelframe(content, text='Options', height=100, width=250)

    self.savePath = ''
    self.defaultImagePath = 'images/default.png'
    self.imagePath = self.defaultImagePath
    self.origImage = cv.imread(self.defaultImagePath)
    self.image = self.origImage.copy()

    removeImageButton = ttk.Button(buttonFrame, text='Remove image...', command=self.removeImage)
    chooseImagePathButton = ttk.Button(buttonFrame, text='Choose image...', command=self.chooseImage)
    chooseSavePathButton = ttk.Button(buttonFrame, text='Choose where to save...', command=self.chooseSavePath)
    aug = tk.StringVar()
    notransRadio = ttk.Radiobutton(transFrame, text='None', variable=aug, value='none', command=self.noTransform)
    vflipRadio = ttk.Radiobutton(transFrame, text='Vertical Flip', variable=aug, value='vflip', command=self.vflip)
    hflipRadio = ttk.Radiobutton(transFrame, text='Horizontal Flip', variable=aug, value='hflip', command=self.hflip)
    self.deg = tk.StringVar()
    self.degEntry = ttk.Entry(transFrame, textvariable=self.deg)
    self.deg.trace_add('write', self.rotate)
    rotateRadio = ttk.Radiobutton(transFrame, text='Rotate', variable=aug, value='rotate', command=lambda: self.enableEntry(self.degEntry))
    self.sd = tk.StringVar()
    self.sdSlider = ttk.Scale(transFrame, variable=self.sd, length=100, from_=0.0, to=1.5)
    self.sdSlider.set(0)
    self.sd.trace_add('write', self.addNoise)
    noiseRadio = ttk.Radiobutton(transFrame, text='Add random Gaussian noise', 
      variable=aug, value='noise', 
      command=lambda: self.enableEntry(self.sdSlider)
    )
    saveButton = ttk.Button(content, text='Save Image', command=self.saveImage)

    content.grid(column=0, row=0)
    imageFrame.grid(column=0, row=0, columnspan=4, rowspan=3, padx=8, pady=5)
    self.imageLabel.grid(column=0, row=0)
    imageSize.grid(column=0, row=1, pady=5)
    transFrame.grid(column=0, row=3, columnspan=2, rowspan=5, padx=8, pady=5, sticky=(tk.N, tk.W))
    buttonFrame.grid(column=2, row=3, columnspan=2, rowspan=3, padx=8, pady=5, sticky=(tk.N, tk.W))
    notransRadio.grid(column=0, row=0, sticky=(tk.N, tk.W))
    vflipRadio.grid(column=0, row=1, sticky=(tk.N, tk.W))
    hflipRadio.grid(column=0, row=2, sticky=(tk.N, tk.W))
    rotateRadio.grid(column=0, row=3, sticky=(tk.N, tk.W))
    self.degEntry.grid(column=0, row=4)
    self.degEntry.state(['disabled'])
    noiseRadio.grid(column=0, row=5, sticky=(tk.N, tk.W))
    self.sdSlider.grid(column=0, row=6)
    self.sdSlider.state(['disabled'])
    removeImageButton.grid(column=0, row=0, sticky=(tk.N, tk.W))
    removeImageButton.invoke()
    chooseImagePathButton.grid(column=0, row=1, sticky=(tk.N, tk.W))
    chooseSavePathButton.grid(column=0, row=2, sticky=(tk.N, tk.W))
    saveButton.grid(column=0, row=8, padx=5, pady=5, columnspan=4)

  def loadImage(self, img):
    h, w = img.shape[:2]
    fname = os.path.basename(self.imagePath)
    self.fileText.set(' ' + fname + ', ' + str(h) + 'x' + str(w) + ' ')
    imgtk = displayImg(img)
    self.imageLabel.configure(image=imgtk)
    self.imageLabel.photo_ref = imgtk # important

  def chooseImage(self):
    self.imagePath = fd.askopenfilename()
    if self.imagePath:
      self.origImage = cv.imread(self.imagePath)
      self.image = self.origImage.copy()
      self.loadImage(self.image)

  def chooseSavePath(self):
    self.savePath = fd.askdirectory()

  def saveImage(self):
    imageFileName = os.path.basename(self.imagePath)
    fileWoExtn, extn = imageFileName.split('.')
    if self.savePath == '':
      messagebox.showerror(title='Error', message='Please first select the destination folder of the saved image...')
    else:
      cv.imwrite(self.savePath + '/' + fileWoExtn + '_aug.' + extn, self.image)
      messagebox.showinfo(title='Image saved', message='Your augmented image was saved successfully!')

  def removeImage(self):
    self.imagePath = self.defaultImagePath
    self.origImage = cv.imread(self.imagePath)
    self.image = self.origImage.copy()
    self.loadImage(self.image)

  def noTransform(self):
    self.disableEntry(self.degEntry)
    self.disableEntry(self.sdSlider)
    self.image = self.origImage.copy()
    self.loadImage(self.image)

  def vflip(self):
    self.disableEntry(self.degEntry)
    self.disableEntry(self.sdSlider)
    self.image = self.origImage.copy()
    self.image = cv.flip(self.image, 0)
    self.loadImage(self.image)

  def hflip(self):
    self.disableEntry(self.degEntry)
    self.disableEntry(self.sdSlider)
    self.image = self.origImage.copy()
    self.image = cv.flip(self.image, 1)
    self.loadImage(self.image)

  def enableEntry(self, entry):
    self.image = self.origImage.copy()
    self.loadImage(self.image)
    entry.state(['!disabled'])
  
  def disableEntry(self, entry):
    entry.state(['disabled'])

  def rotate(self, *args):
    self.disableEntry(self.sdSlider)
    self.image = self.origImage.copy()
    try:
      if self.deg.get() != '':
        degrees = float(self.deg.get())
      else:
        degrees = 0.0
      h, w = self.image.shape[:2]
      rotationMat = cv.getRotationMatrix2D((w//2, h//2), degrees, 1.0)
      self.image = cv.warpAffine(self.image, rotationMat, (w, h))
      self.loadImage(self.image)
    except:
      pass

  def addNoise(self, *args):
    self.disableEntry(self.degEntry)
    self.image = self.origImage.copy()
    stdDev = float(self.sd.get())
    gauss = np.random.normal(0, stdDev, self.image.size)
    h, w, c = self.image.shape
    gauss = gauss.reshape(h, w, c).astype('uint8')
    self.image = cv.add(self.image, gauss)
    self.loadImage(self.image)

root = tk.Tk()
root.title('Transformer')
root.geometry('515x700')
root.minsize(515, 730)

def closeWindow(*args):
  close = messagebox.askyesno(
    message='Are you sure you want to close the application?',
    icon='warning', title='Close'
  )
  if close:
    root.destroy()

root.protocol('WM_DELETE_WINDOW', closeWindow)
Transformations(root)
root.mainloop()
