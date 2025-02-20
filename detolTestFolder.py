import cv2
import argparse
import numpy as np
import glob
from timeit import default_timer as timer

ap = argparse.ArgumentParser()
ap.add_argument('-c', '--config', 
                help = 'path to config file', default="/home/ignitarium/Desktop/boxing/yolov3-tiny.cfg")
ap.add_argument('-w', '--weights', 
                help = 'path to pre-trained weights', default="/home/ignitarium/Desktop/boxing/yolov3-tiny_final.weights")
ap.add_argument('-cl', '--classes', 
                help = 'path to objects.names',default="/home/ignitarium/Desktop/boxing/objects.names")
args = ap.parse_args()


# Get names of output layers, output for YOLOv3 is ['yolo_16', 'yolo_23']
def getOutputsNames(net):
    layersNames = net.getLayerNames()
    return [layersNames[i[0] - 1] for i in net.getUnconnectedOutLayers()]


# Darw a rectangle surrounding the object and its class name 
def draw_pred(img, class_id, confidence, x, y, x_plus_w, y_plus_h):

    label = str(classes[class_id])

    color = COLORS[class_id]

    cv2.rectangle(img, (x,y), (x_plus_w,y_plus_h), (0,0,255), 2)

    cv2.putText(img, label, (x-10,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2)
    
# Define a window to show the cam stream on it
#window_title= "Hole Detector"   
#cv2.namedWindow(window_title, cv2.WINDOW_NORMAL)


# Load names classes
classes = None
with open(args.classes, 'r') as f:
    classes = [line.strip() for line in f.readlines()]
print(classes)

#Generate color for each class randomly
COLORS = np.random.uniform(0, 255, size=(len(classes), 3))

# Define network from configuration file and load the weights from the given weights file
net = cv2.dnn.readNet(args.weights,args.config)

# Define video capture for default cam
#cap = cv2.VideoCapture(0)


#while cv2.waitKey(1) < 0 or False:
    
 #   hasframe, image = cap.read()

#image=cv2.imread('/home/mostafiz/Documents/Tower/yolo-custom-object-detector_new/Detol/frame426.jpg',-1)

## Path to the image folder
path='/home/ignitarium/Desktop/boxing/front_jpg//*.jpg'

detecHole=0

#rects=[]
for file in sorted(glob.glob(path)):
    ## Reading the whole 5472x3078 image
    image=cv2.imread(file)
    start = timer()
     ## Preparation for outname generation
    name=file.split('/')
    outName=name[-1].split('.')
    
    blob = cv2.dnn.blobFromImage(image, 1.0/255.0, (416,416), [0,0,0], True, crop=False)
    Width = image.shape[1]
    Height = image.shape[0]
    net.setInput(blob)
    
    outs = net.forward(getOutputsNames(net))
    
    class_ids = []
    confidences = []
    boxes = []
    conf_threshold = 0.5
    nms_threshold = 0.9
    
    
    #print(len(outs))
    
    # In case of tiny YOLOv3 we have 2 output(outs) from 2 different scales [3 bounding box per each scale]
    # For normal normal YOLOv3 we have 3 output(outs) from 3 different scales [3 bounding box per each scale]
    
    # For tiny YOLOv3, the first output will be 507x6 = 13x13x18
    # 18=3*(4+1+1) 4 boundingbox offsets, 1 objectness prediction, and 1 class score.
    # and the second output will be = 2028x6=26x26x18 (18=3*6) 
    
    for out in outs: 
    #print(out.shape)
        for detection in out:
            
   
            scores = detection[5:]#classes scores starts from index 5
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                center_x = int(detection[0] * Width)
                center_y = int(detection[1] * Height)
                w = int(detection[2] * Width)
                h = int(detection[3] * Height)
                x = center_x - w / 2
                y = center_y - h / 2
                class_ids.append(class_id)
                confidences.append(float(confidence))
                boxes.append([x, y, w, h])
    
    # apply non-maximum suppression algorithm on the bounding boxes
    indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)
    
    for i in indices:
        i = i[0]
        box = boxes[i]
        x = box[0]
        y = box[1]
        w = box[2]
        h = box[3]
        image = image[y:y+h, x:(x+w),:]
        #draw_pred(image, class_ids[i], confidences[i], round(x), round(y), round(x+w), round(y+h))
   		
    # Put efficiency information.
   # t, _ = net.getPerfProfile()
    #label = 'Inference time: %.2f ms' % (t * 1000.0 / cv2.getTickFrequency())
    end = timer()  
    print('time = ', end-start, 'sec')
    #cv2.putText(image, label, (0, 15), cv2.FONT_HERSHEY_SIMPLEX, .6, (255, 0, 0))
    path1='/home/ignitarium/Desktop/boxing/Result_1/'+str(outName[0])+str('_out')+str('.JPG')     
    print(detecHole)
    detecHole=detecHole+1
    cv2.imwrite(path1,image) 
#cv2.imshow(window_title, image)
#cv2.waitKey(2000)
