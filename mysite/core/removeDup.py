import os
from math import sqrt
from os.path import join
import cv2
import numpy as np
import shutil
from skimage.metrics import structural_similarity

def getGreyImgs(Path, greyDir):
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

def main():
    Path = os.getcwd() + "/images"
    greyDir = join(Path, "greyImg")
    os.makedirs(greyDir)

    # Function to grey out the images and store them in greyDir
    # getGreyImgs(Path, greyDir)

    # Function to compare images based on RMS and SSM
    # FindNRemoveGreyDupli(greyDir)

    # Remove duplicate from actual directory
    # RemoveDupli(greyDir, Path)

    # Remove greyscaled images directory
    # shutil.rmtree(greyDir)

if __name__ == "__main__":
    main()