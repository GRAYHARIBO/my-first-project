import matplotlib.pyplot as plt
import numpy as np
import time
from pyrplidar import PyRPlidar

PORT_NUM = "COM5"   # Fix Me
MAX_DATA = 2000   # 2000마다 데이터 띄움
DIS_UP = 1000   # 1000mm
DIS_DOWN = 50
ANGLE_UP = 45
ANGLE_DOWN = -45    

# LiDAR & Camera Fusion====================================================
def thetar2pix(rtheta):   # return pixel(u,v) and distance

    #Filtering Data-----------------------------------------------------------

    thetamin = 45; thetamax = 315  #FOV [Degrees]
    rmin = DIS_DOWN; rmax = DIS_UP  #Distance [mm] 

    for i in range(rtheta.shape[0]):
        if (rtheta[i,0] > thetamin) and (rtheta[i,0] < thetamax):
            rtheta[i,:] = np.nan

    rtheta[:,0] = -rtheta[:,0]*np.pi/180  #degree to radian

    for i in range(np.shape(rtheta)[0]):
        if (rtheta[i,1] < rmin) or (rtheta[i,1] >= rmax):
            rtheta[i,:] = np.nan 


    #Polar -> Cartesian-------------------------------------------------------

    y_s = 0     #lidar height set to 0
    
    coor = np.zeros(rtheta.shape) #(x*,y*,z*) [mm]
    for i in range(rtheta.shape[0]):
        if rtheta[i,0] == np.nan:
            coor[i,:] = np.nan
        else:
            coor[i,0] = -rtheta[i,1]*np.sin(rtheta[i,0])
            coor[i,1] = y_s
            coor[i,2] = rtheta[i,1]*np.cos(rtheta[i,0])
    
    trans_vec = [0,80,0]     #lidar to camera vector

    for i in range(3):
        coor[:,i] = coor[:,i] + trans_vec[i]    #to camera 3D space


    #Cartesian -> Pixel-------------------------------------------------------

    #1920x1080
    cam_mat1 = [[1.39697095e+03, 0.00000000e+00, 1.00983541e+03],
    [0.00000000e+00, 1.39632273e+03, 5.26933739e+02],
    [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]]


    #640x480
    cam_mat2 = [[622.39801669,   0,         327.82995341],
    [  0,         617.28766013, 261.42463435],
    [  0,           0           , 1        ]]
    
    pix_coor = np.zeros(rtheta.shape)
    pix = np.zeros((rtheta.shape[0],2))    #pixel space

    for i in range(rtheta.shape[0]):   #(x,y,z) to (u,v)
        pix_coor[i,2] = coor[i,2]
        pix_coor[i,0] = cam_mat2[0][0]*coor[i,0] + cam_mat2[0][2]*coor[i,2]
        pix_coor[i,1] = cam_mat2[1][1]*coor[i,1] + cam_mat2[1][2]*coor[i,2]
        
        pix[i,0] = pix_coor[i,0]/pix_coor[i,2]
        pix[i,1] = pix_coor[i,1]/pix_coor[i,2]
    
    return pix, rtheta[:,1]


if (__name__ == '__main__'):
    #Lidar -> theta, r =====================================================

    rpm = 0
    lidar = PyRPlidar()
    ang=np.array([0])
    dis=np.array([0]) 

    # yield data.T (= np.array([ang,dis])의 전치행렬)
    ang=np.array([0])
    dis=np.array([0])

    ##### Lidar Initialize #####
    lidar.connect(port=PORT_NUM, baudrate=115200, timeout=3) 
    lidar.set_motor_pwm(660)
    scan_generator = lidar.start_scan_express(3)

    ###### plot initialize #####
    plt.ion()
    fig = plt.figure(figsize=(8,8))
    ax = fig.add_subplot(projection='polar')
    plt.title('Graph Title', fontweight='bold', fontsize=20)
    plt.ylim(0,DIS_UP)
    c = ax.scatter(ang,dis, c='red', s=5)

    ###### Loop ######
    for scan in scan_generator():
        scan = vars(scan)
        angle = np.array(scan["angle"])
        distance = np.array(scan["distance"])
        # print("Angle= " + str(angle) + ", Distance= " + str(distance))

        if len(ang) > MAX_DATA :
            ###### plot update #####
            fig.canvas.flush_events()
            ax.cla()
            c = ax.scatter((-ang-90)*np.pi/180,dis, c='red', s=5)
            plt.ylim(0,DIS_UP)
            plt.title('Graph Title', fontweight='bold', fontsize=20)
            plt.title("Time : " + str(time.strftime('%M:%S', time.localtime(time.time()))), loc='right', pad=20)  ## +" / Count : " +str(count)
            ax.plot(np.array([ANGLE_UP,0])*np.pi/180, [DIS_UP,0], color='b', linewidth=2, linestyle='solid') ## range bar
            ax.plot(np.array([ANGLE_DOWN,0])*np.pi/180, [DIS_UP,0], color='b', linewidth=2, linestyle='solid') ## range bar
            fig.canvas.draw()
            
            data=np.array([(-ang-90),dis])
            x=data.T

            ang=np.array([0])
            dis=np.array([0])
        else :
            ang = np.append(ang, angle)
            dis = np.append(dis, distance)



        