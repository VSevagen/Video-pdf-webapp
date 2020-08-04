from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView, CreateView
from django.utils.encoding import smart_str
from django.http import HttpResponse, Http404
from django.core.files.storage import FileSystemStorage
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

from .forms import BookForm
from .models import Book


class Home(TemplateView):
    template_name = 'home.html'


def upload(request):
    context = {}
    if request.method == 'POST':
        uploaded_file = request.FILES['document']
        fs = FileSystemStorage()
        name = fs.save(uploaded_file.name, uploaded_file)
        video_process(uploaded_file)
        removeDup()
        makepdf()
        download(request)
        context['url'] = fs.url(name)
    return render(request, 'upload.html', context)

def video_process(uploaded_file):
    path = join(os.getcwd(), "media/"+uploaded_file.name)
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

def makepdf():
    path = os.getcwd()+"/images"
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


def download(request):
    fl_path = os.getcwd()+"/output.pdf"
    filename = 'output.pdf'

    file_path = os.path.join(settings.MEDIA_ROOT, fl_path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/pdf")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404










def book_list(request):
    books = Book.objects.all()
    return render(request, 'book_list.html', {
        'books': books
    })


def upload_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm()
    return render(request, 'upload_book.html', {
        'form': form
    })


def delete_book(request, pk):
    if request.method == 'POST':
        book = Book.objects.get(pk=pk)
        book.delete()
    return redirect('book_list')


class BookListView(ListView):
    model = Book
    template_name = 'class_book_list.html'
    context_object_name = 'books'


class UploadBookView(CreateView):
    model = Book
    form_class = BookForm
    success_url = reverse_lazy('class_book_list')
    template_name = 'upload_book.html'