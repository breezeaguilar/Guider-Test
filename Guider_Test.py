import cv2
import math
import time

CAM_CENTER_X = -1
CAM_CENTER_Y = -1
SUN_X = -1
SUN_Y = -1

def calculate_coord(img, display=False, scale=1, blur=1):
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    n=scale
    k=blur
    img_gray = cv2.resize(img_gray,(0,0),fx=1/n,fy=1/n)
    img_gray = cv2.blur(img_gray,(k,k))
    ret, img_thresh = cv2.threshold(img_gray, 250, 255, cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(img_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    a_act = 0
    b_act = 0
    w_act = 0
    h_act = 0
    largestarea = 0.0
    i=0
    if(len(contours)>0):
            for c in contours:
                    area = cv2.contourArea(c)
                    
                    a,b,w,h = cv2.boundingRect(c)
                    if(display): print("Run #: ", i,"a: ",a,"b: ",b,"w: ",w,"h: ",h)
                    
                    i+=1
                                    
                    if (area > largestarea):
                            largestarea = area
                            M_1= cv2.moments(c)
                            if M_1["m00"] == 0: M_1["m00", "m01"] = 1
                            x = int(M_1["m10"] / M_1["m00"])
                            y = int(M_1["m01"] / M_1["m00"])
                            a_act = a
                            b_act = b
                            w_act = w
                            h_act = h
                    
                            cv2.rectangle(img_gray,(int(a_act),int(b_act)),(int(a_act+w_act),int(b_act+h_act)),(0,255,0),2)
            if largestarea==0:return None,None,None,None,n,k,i
            
            ex = x - img_gray.shape[1] / 2
            ey = y - img_gray.shape[0] / 2
            
            x*=n
            y*=n
            ex*=n
            ey*=n
            return ex, ey, x, y, n, k, i
    return None,None,None,None,n,k,None

def GetSunPosition(DeltaGMT : float, NumberOfDays : int, LocalTime : float, Longitude : float, Latitude : float) -> tuple:
    # DeltaGMT is in hours
    # LocalTime is in hours
    LocalStandardTimeMeridian = 15 * DeltaGMT   # hours
    B = (360 / 365) * (NumberOfDays - 81)   # degrees
    EquationOfTime = 9.87 * math.sin(2 * math.radians(B)) - 7.53 * math.cos(math.radians(B)) - 1.5 * math.sin(math.radians(B))  # minutes
    TimeCorrection = 4 * (Longitude - LocalStandardTimeMeridian) + EquationOfTime   # minutes
    LocalSolarTime = LocalTime + TimeCorrection / 60    # hours
    HourAngle = 15 * (LocalSolarTime - 12)  # degrees
    Declanation = 23.45 * math.sin((math.radians(360/365)) * (NumberOfDays - 81))   # degrees
    Elevation = math.asin(math.sin(math.radians(Declanation)) * math.sin(math.radians(Latitude)) + math.cos(math.radians(Declanation)) * math.cos(math.radians(Latitude)) * math.cos(math.radians(HourAngle)))  # radians
    Azimuth = math.acos(((math.sin(math.radians(Declanation)) * math.cos(math.radians(Latitude))) - (math.cos(math.radians(Declanation)) * math.sin(math.radians(Latitude)) * math.cos(math.radians(HourAngle)))) / math.cos(math.radians(Elevation)))  # radians
    return math.degrees(Elevation), math.degrees(Azimuth)

def get_check_sum(b: bytearray) -> bytes:
    c = 0
    for byte in b:
        c+=byte
    return c.to_bytes(math.ceil(math.log2(c)/8), "big")[-1:]

def step(max, min, threshold, val):
    if(val>=threshold):
        return min
    else:
        return max

'''
def get_cam_center(img):
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    CAM_CENTER_X = img_gray.size[1] / 2
    CAM_CENTER_Y = img_gray.size[0] / 2
'''
    
def get_sun_pos(img):
    global SUN_X
    global SUN_Y
    global CAM_CENTER_X
    global CAM_CENTER_Y
    print("gets here 2")
    SUN_X, SUN_Y, CAM_CENTER_X, CAM_CENTER_Y, _, _, _ = calculate_coord(img)

def get_all_pos(): # meant to be called in PID C script with popen: above functions require image argument
    return CAM_CENTER_X, CAM_CENTER_Y, SUN_X, SUN_Y

def drawContour(frame):
    img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    n=1
    k=1
    img_gray = cv2.resize(img_gray,(0,0),fx=1/n,fy=1/n)
    img_gray = cv2.blur(img_gray,(k,k))
    ret, img_thresh = cv2.threshold(img_gray, 250, 255, cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(img_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(frame, contours, -1, (0, 255, 0), 2)
    cv2.imshow("Contours", frame)
    largestarea = 0
    #'''
    for c in contours:
            area = cv2.contourArea(c)

            a,b,w,h = cv2.boundingRect(c)
            # if(display): print("Run #: ", i,"a: ",a,"b: ",b,"w: ",w,"h: ",h)
            # commented out because display is false

            # i+=1         

            if (area > largestarea):
                largestarea = area
                M_1= cv2.moments(c)

                if M_1["m00"] == 0: M_1["m00", "m01"] = 1

                x = int(M_1["m10"] / M_1["m00"])
                y = int(M_1["m01"] / M_1["m00"])
                a_act = a
                b_act = b
                w_act = w
                h_act = h

                cv2.rectangle(img_gray,(int(a_act),int(b_act)),(int(a_act+w_act),int(b_act+h_act)),(0,255,0),2)
                pos = {x, y}
                print(x, ",", y)
    global CAM_CENTER_X, CAM_CENTER_Y
    CAM_CENTER_X = x
    CAM_CENTER_Y = y


def test():
    cam = cv2.VideoCapture(0)
    
    start_time = time.time()
    test_duration = 120

    if not cam.isOpened():
        print("Cannot open camera")
        return

    while time.time() - start_time < test_duration:

        ret, frame = cam.read()

        if not ret:
            print("Could not capture frame")
            cam.release()
            exit()

        # height, width = frame.shape[:2]
        # channels = 1
        # cam_center_x = width // 2
        # cam_center_y = height // 2

        cv2.imshow("Captured Frame", frame)
        key = cv2.waitKey(1)

        if key == ord('p'): # print coordinates, wrong tho, fix later maybe? pressing c should do the same thing
            # print()
            print("gets here")
            pos = get_sun_pos(frame)
            if pos is not None:
                print(f"{pos[0]} {pos[1]} {pos[2]} {pos[3]}")
            else:
                print("Position not found")

        if key == ord('c'): # draw contour to ensure it is found
            img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            n=1
            k=1
            img_gray = cv2.resize(img_gray,(0,0),fx=1/n,fy=1/n)
            img_gray = cv2.blur(img_gray,(k,k))
            ret, img_thresh = cv2.threshold(img_gray, 250, 255, cv2.THRESH_BINARY)
            contours, hierarchy = cv2.findContours(img_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(frame, contours, -1, (0, 255, 0), 2)
            cv2.imshow("Contours", frame)
            largestarea = 0
        #'''
            for c in contours:
                    area = cv2.contourArea(c)

                    a,b,w,h = cv2.boundingRect(c)
                    # if(display): print("Run #: ", i,"a: ",a,"b: ",b,"w: ",w,"h: ",h)
                    # commented out because display is false

                    # i+=1         

                    if (area > largestarea):
                            largestarea = area
                            M_1= cv2.moments(c)

                            if M_1["m00"] == 0: M_1["m00", "m01"] = 1

                            x = int(M_1["m10"] / M_1["m00"])
                            y = int(M_1["m01"] / M_1["m00"])
                            a_act = a
                            b_act = b
                            w_act = w
                            h_act = h

                            cv2.rectangle(img_gray,(int(a_act),int(b_act)),(int(a_act+w_act),int(b_act+h_act)),(0,255,0),2)
                            pos = {x, y}
                            print(x, ",", y)
        #'''
        if key == 27:
            break

    cam.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # test()
    cam = cv2.VideoCapture(0)
    
    start_time = time.time()
    test_duration = 120

    if not cam.isOpened():
        print("Cannot open camera")

    while time.time() - start_time < test_duration:

        ret, frame = cam.read()

        if not ret:
            print("Could not capture frame")
            cam.release()
            exit()

        # height, width = frame.shape[:2]
        # channels = 1
        # cam_center_x = width // 2
        # cam_center_y = height // 2

        cv2.imshow("Captured Frame", frame)
        key = cv2.waitKey(1)

        if key == ord('p'): # print coordinates, wrong tho, fix later maybe? pressing c should do the same thing
            # print()
            print("gets here")
            pos = get_sun_pos(frame)
            if pos is not None:
                print(f"{pos[0]} {pos[1]} {pos[2]} {pos[3]}")
            else:
                print("Position not found")

        if key == ord('c'): # draw contour to ensure it is found, prints coordinates
            drawContour(frame)

        if key == 27:
            break

    cam.release()
    cv2.destroyAllWindows()
