from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView, CreateView
from django.utils.encoding import smart_str
from django.http import HttpResponse, Http404
from django.core.files.storage import FileSystemStorage
from django.views.static import serve
from django.views import View
from django.conf import settings
from django.urls import reverse_lazy
from skimage.metrics import structural_similarity
import cv2
import mimetypes
import shutil
import img2pdf
import os
from os.path import join
import numpy as np


class Home(TemplateView):
    template_name = 'home.html'

def upload(request):
    context = {}
    if request.method == 'POST':
        if myfun() > 1:
            os.chdir('..')
        uploaded_file = request.FILES['document']
        request.session['file'] = uploaded_file.name
        fs = FileSystemStorage()
        name = fs.save(uploaded_file.name, uploaded_file)
        context['url'] = fs.url(name)
    return render(request, 'upload.html', context)

def video_process(request):
    uploaded_file = request.session['file']
    path = join(os.getcwd(), "media/"+uploaded_file)
    Path = os.getcwd() + "/images"
    vidcap = cv2.VideoCapture(path)
    def getFrame(sec):
        vidcap.set(cv2.CAP_PROP_POS_MSEC,sec*1000)
        hasFrames,image = vidcap.read()
        if hasFrames:
            print(str(count)+".jpg")
            if not cv2.imwrite(join(Path,str(count)+".jpg"), image):
                raise Exception("Could not write image") 
        return hasFrames
    sec = 0
    frameRate = 1
    count=1
    success = getFrame(sec)
    while success:
        count = count + 1
        sec = sec + frameRate
        sec = round(sec, 2)
        success = getFrame(sec)

    removeDup()
    return render(request, 'images.html')



def removeDup():
    Path = os.getcwd() + "/images"
    greyDir = join(Path, "greyImg")
    os.makedirs(greyDir)

    def getGreyImgs(Path, GreyDir):
        for(j, imgName) in enumerate(os.listdir(Path)):
            # Get path of image
            imagePath = join(Path, imgName)

            # Convert the image to greyscale
            image = cv2.imread(imagePath, cv2.IMREAD_GRAYSCALE) 

            # Resize image to 32x32 and store them in greyDir
            if image is not None:
                resizeImage = cv2.resize(image, (32, 32))
                resizeImage = np.array(resizeImage)
                cv2.imwrite(os.path.join(greyDir, imgName), resizeImage)

    def FindNRemoveGreyDupli(greyDir):
        fnames = sorted([fname for fname in os.listdir(greyDir) if fname.endswith('.jpg')], key=lambda f: int(f.rsplit(os.path.extsep, 1)[0].rsplit(None,1)[-1]))
        for(i, greyImg) in enumerate(fnames):
            # Take first image for comparing
            searchedImg = join(greyDir, greyImg)

            for(j, ImgCompare) in enumerate(os.listdir(greyDir)):
                # Check whether we are comparing same image as above. In that
                # case, we skip it.
                if ImgCompare == greyImg:
                    pass
                else:
                    # Not same image so we take it for comparision
                    ImgCompareGrey = join(greyDir, ImgCompare)
                    try:
                        # Open the image in terms of a matrix of rgb
                        FinalSearchedImg = np.array(cv2.imread(searchedImg, cv2.IMREAD_GRAYSCALE))
                        FinalCompareImg = np.array(cv2.imread(ImgCompareGrey, cv2.IMREAD_GRAYSCALE))

                        # Calculate Root-Mean_Square
                        # rms = sqrt(mean_squared_error(FinalSearchedImg, FinalCompareImg ))

                        # Calculate structural similarity
                        h = structural_similarity(FinalSearchedImg, FinalCompareImg)

                    except:
                        continue
                    if h > 0.9:
                        # Remove duplicate image
                        os.remove(searchedImg)
                        print (searchedImg, ImgCompareGrey, h)  

    def RemoveDupli(greyDir, Path):
        greyImg = os.listdir(greyDir)

        for img in os.listdir(Path):
           if img not in greyImg and img != 'greyImg':
               os.remove(os.path.join(Path, img))                    

    getGreyImgs(Path, greyDir)
    FindNRemoveGreyDupli(greyDir)
    RemoveDupli(greyDir, Path)
    shutil.rmtree(greyDir)
    copytree(os.getcwd()+"/images", os.getcwd()+"/test")
    makepdf()

def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)

def raw_remove(request):
    os.chdir('..')
    path = os.getcwd() + "/test"
    os.chdir(path)
    myimages = []
    dirFiles = os.listdir(os.getcwd())
    fnames = sorted([fname for fname in os.listdir(os.getcwd()) if fname.endswith('.jpg')], key=lambda f: int(f.rsplit(os.path.extsep, 1)[0].rsplit(None,1)[-1]))

    for(i, image) in enumerate (fnames):
        for(i, imageCom)in enumerate (fnames):
            if image == imageCom:
                pass
            else:
                try:
                    searchedImg = cv2.imread(image)
                    ImgCompareGrey = cv2.imread(imageCom)
                    FinalSearchedImg = cv2.cvtColor(searchedImg, cv2.COLOR_BGR2GRAY)
                    FinalCompareImg = cv2.cvtColor(ImgCompareGrey, cv2.COLOR_BGR2GRAY)
                    h = structural_similarity(FinalSearchedImg, FinalCompareImg)
                except:
                    continue
                if h > 0.87:
                    os.remove(image)
                    print(image, imageCom, h)
    makepdf2()
    return render(request, 'eliminate.html')

def makepdf2():
    path = os.getcwd()
    os.chdir(path)
    myimages = []
    dirFiles = os.listdir(os.getcwd())
    fnames = sorted([fname for fname in os.listdir(os.getcwd()) if fname.endswith('.jpg')], key=lambda f: int(f.rsplit(os.path.extsep, 1)[0].rsplit(None,1)[-1]))
    with open("output.pdf", "wb") as f:
        f.write(img2pdf.convert([i for i in fnames if i.endswith(".jpg")]))

    imgDir = os.listdir(path)
    for image in imgDir:
        if image.endswith(".jpg"):
            os.remove(os.path.join(path, image))

def makepdf():
    path = os.getcwd() + "/images"
    os.chdir(path)
    myimages = []
    dirFiles = os.listdir(os.getcwd())
    fnames = sorted([fname for fname in os.listdir(os.getcwd()) if fname.endswith('.jpg')], key=lambda f: int(f.rsplit(os.path.extsep, 1)[0].rsplit(None,1)[-1]))
    with open("output.pdf", "wb") as f:
        f.write(img2pdf.convert([j for j in fnames if j.endswith(".jpg")]))

    imgDir = os.listdir(path)
    for image in imgDir:
        if image.endswith(".jpg"):
            os.remove(os.path.join(path, image))


def download(request):
    fl_path = os.getcwd() + "/output.pdf"
    return serve(request, os.path.basename(fl_path),os.path.dirname(fl_path))

def myfun(i=[0]):
    i[0]+=1
    return i[0]