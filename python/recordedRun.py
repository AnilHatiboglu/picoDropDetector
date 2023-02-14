import cv2
import numpy as np
import math
import imutils
import matplotlib.pyplot as plt



def player(fname, minR, maxR, check, ):
    cap = cv2.VideoCapture(fname)
    minR = int(minR)
    maxR = int(maxR)
    check = bool(check)
    fname = fname.replace(".avi","")
    scale = 1757.80  #4x kamera icin
    #scale = 703.12  #10x kamera icin
    #scale = 351.56  #20x kamera icin
    #scale = 175.78  #40x kamera icin

    totalFrame = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print (totalFrame)
    font = cv2.FONT_HERSHEY_SIMPLEX
    height = 1200
    width  = 1600

    cnt = 0

    ''' ONEMLI !!!!!
    Algoritmanin daha hassas olcebilmesi icin, olcmek istedigimiz maximum ve minimum araligin daraltilmasi gerekmektedir. 
    Mikrometre cinsinden asagida duzenlenmelidir. 
    '''
      

    MaxOfInterest = 80 # in micrometers
    MinOfInterest = 60 # in micrometers

    ''' ONEMLI !!!!!
    4x  kamera icin asagidaki max-minOfInterest yazan yerleri 1600/1757.80 ile carpiyoruz.
    10x kamera icin asagidaki max-minOfInterest yazan yerleri 1600/703.12 ile carpiyoruz.
    ''' 
    maxR = int(maxR*1600/1757.80) # in pixels
    minR = int(minR*1600/1757.80) # in pixels

    ''' ONEMLI !!!!! 
    Asagidaki text dosyasina butun damlaciklarin diameterleri satir satir kayit edilecek. Uygun bir dosya ismi yeterli.
    '''

    file1 = open("droplet"+fname+"-Droplet.txt", "w")
    file2 = open("droplet"+fname+"-Distance.txt", "w")

    dropletList = []
    distanceList = []
    centerDistanceList = []
    while True:
        ret,frame = cap.read()
        cnt = cnt + 1
        
        frame = cv2.medianBlur(frame,5)
        
        cimg = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        circles = cv2.HoughCircles(cimg,cv2.HOUGH_GRADIENT,1,maxR, param1=50,param2=30,minRadius=minR,maxRadius=maxR)
        print ("--------------------------------------------")
        print ("Frame", cnt, "of", totalFrame)
        print (circles)

        if circles is not None:
            circles=circles
            circles=np.uint16(np.around(circles))
            count = 0
            tempList = []
            tempDiameter = []
            
            for i in circles[0,:]:
                
                cv2.circle(cimg, (maxR, maxR), minR, (0,0,0), 2)
                cv2.circle(cimg, (maxR, maxR), maxR, (0,0,0), 2)
                cv2.putText(cimg, str("Largest & Smallest"), (maxR+100, maxR), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0),2)
                cv2.putText(cimg, str("Detectable Circles"), (maxR+100, maxR+50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0),2)
                # draw the outer circle
                cv2.circle(cimg, (i[0], i[1]), i[2], (0,0,0), 2)
                #draw the center of the circle
                cv2.circle(cimg, (i[0], i[1]), 2, (0,0,0), 3)
    
                diameter = (2*i[2]*scale/1600)
                displayDiameter = truncate(diameter,3)
                print ("Diameter: ", diameter)
                dropletList.append(diameter)

                distance = (i[0]*scale/1600)
                tempList.append(distance)
                tempDiameter.append(diameter)
                print(tempList)
                tempList = sorted(tempList)
                tempDiameter = sorted(tempDiameter)
                #print(tempList)
                cv2.putText(cimg, str(displayDiameter), (i[0]-60, i[1]-80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0),2)
                cv2.putText(cimg, str("FileName:"+fname), (400, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0),2)
                cv2.putText(cimg, str("Droplet Diameter [um]"), (750, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0),2)
                cv2.putText(cimg, str("Interdroplet Distance [um]"), (1150, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0),2)
                cv2.putText(cimg, str("_____________________"), (750, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0),2)
                cv2.putText(cimg, str(displayDiameter), (750, count*50+90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0),2)
                file1.write(repr(diameter)+"\n")
                count = count+1
                

            for x in range(len(tempList)-1):
               
                if abs(tempList[x+1]-tempList[x])<1500:
                    file2.write(repr(abs(tempList[x+1]-tempList[x]))+"\n ")
                    distanceList.append(abs(tempList[x+1]-tempList[x])-(tempDiameter[x+1]/2+tempDiameter[x]/2))
                    centerDistanceList.append(abs(tempList[x+1]-tempList[x]))
                    displayDistance = truncate(abs(tempList[x+1]-tempList[x])-(tempDiameter[x+1]/2+tempDiameter[x]/2),3)
                    print ("Distance \n", abs(tempList[x+1]-tempList[x])-(tempDiameter[x+1]/2+tempDiameter[x]/2))
                    cv2.putText(cimg, str("Interdroplet Distance [um]"), (1150, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0),2)
                    cv2.putText(cimg, str("__________________________"), (1150, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0),2)
                    cv2.putText(cimg, str(displayDistance), (1150, x*50+90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0),2)


        if check == False:
            cv2.imshow('Frame', cimg)

        if cnt == totalFrame-1:
            break
        if cv2.waitKey(300) & 0xFF == ord('q') | cnt==10:
            break
    cap.release()
    cv2.destroyAllWindows()
    file1.close()
    file2.close()
    ''' ONEMLI !!!!! 
    Asagidaki text dosyasina toplam damlacik sayisi, ortalama deger gibi bilgiler kayit edilecek. Uygun bir dosya ismi yeterli.
    '''
    file = open("droplet"+fname+"-Report.txt", "w")
    file.write( "Number of Frames: " + repr(totalFrame))

    file.write("\n Average Droplet Size: " + repr(np.mean(dropletList)))
    file.write("\n total droplet amount: " + repr(len(dropletList)))

    file.write("\n Average Droplet Distance: " + repr(np.mean(distanceList)))
    file.write("\n total droplet distance amount: " + repr(len(distanceList)))
    
    file.close()

    fig, ax1 = subplots()
    ax2 = ax1.twinx()
    ''' ONEMLI !!!!! 
    Asagidaki resim dosyasina sonucun grafigi cikarilacak. Uygun bir dosya ismi yeterli.
    '''
    bins = np.linspace(MinOfInterest*2, MaxOfInterest*2, MaxOfInterest*2-MinOfInterest*2+1)
    plt.hist(dropletList, bins, alpha=0.5, label='Droplets @ 25 Celcius')
    plt.xlabel('Droplet Diameter [um]', fontsize=8)
    plt.ylabel('Number of Droplets', fontsize=8)
    plt.legend(loc='upper right')
    plt.savefig(fname+"-Histogram.png")
    plt.clf()

    x1 = np.arange(1,len(distanceList)+1)
    x2 = np.arange(1,len(centerDistanceList)+1)
    x3 = np.arange(1,len(dropletList)+1)
    ax1.plt.plot(x1, distanceList,'.', label='Distance from the surfaces')
    ax1.plt.plot(x2, centerDistanceList,'.', label='Distance from the centers')
    ax2.plt.plot(x3, dropletList, '.')
    ax1.set_xlabel('Droplet Number (based on the detection order)', fontsize=8)
    ax1.set_ylabel('Interdroplet Distance [um]', fontsize=8)
    ax2.set_ylabel("Droplet Size [um]")
    plt.legend(loc='upper right')
    plt.savefig(fname+"-InterDropletDistance.png")
    plt.figure()
    plt.plot(x3, dropletList,'.')
    plt.show()
    
def truncate(f, n):
    '''Truncates/pads a float f to n decimal places without rounding'''
    s = '{}' .format(f)
    if 'e' in s or 'E' in s:
        return '{0:.{1}f}'.format(f, n)
    i, p, d = s.partition('.')
    return '.'.join([i, (d+'0'*n)[:n]])