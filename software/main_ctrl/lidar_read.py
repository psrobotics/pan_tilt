import tkinter as tk
import math
import serial
import time
from ctypes import *

#pan_device = serial.Serial('COM11', 9600)
#time.sleep(2)
#print("Connection to arduino...")

dll = windll.LoadLibrary('F:\projects-3\pan_tilt\software\main_ctrl\ControlCAN.dll')
nDeviceType = 4     #USBCAN-2 device
nDeviceInd = 0      #linker 0
nReserved = 0
nCANInd = 0         #can port 0

class _VCI_INIT_CONFIG(Structure):
    _fields_ = [("AccCode", c_ulong), ("AccMask", c_ulong), ("Reserved", c_ulong), ("Filter", c_ubyte),
                ("Timing0", c_ubyte), ("Timing1", c_ubyte), ("Mode", c_ubyte)]
class _VCI_CAN_OBJ(Structure):
    _fields_ = [("ID", c_uint), ("TimeStamp", c_uint), ("TimeFlag", c_ubyte), ("SendType", c_ubyte),
                ("RemoteFlag", c_ubyte), ("ExternFlag", c_ubyte), ("DataLen", c_ubyte), ("Data", c_ubyte*8),
                ("Reserved", c_ubyte*3)]

vic = _VCI_INIT_CONFIG()
vic.AccCode = 0x80000000
vic.AccMask = 0xffffffff
vic.Filter = 0
vic.Timing0 = 0x00
vic.Timing1 = 0x1c
vic.Mode = 0

vco = _VCI_CAN_OBJ()
vco.ID = 0x00000001
vco.SendType = 0
vco.RemoteFlag = 0
vco.ExternFlag = 0
vco.DataLen = 8
vco.Data = (1, 2, 3, 4, 5, 6, 7, 8)

vco2 = _VCI_CAN_OBJ()

#ubyte_array8 = c_ubyte*8
#ubyte_array3 = c_ubyte*3
vco2.ID = 0x00000001
vco2.SendType = 0
vco2.RemoteFlag = 0
vco2.ExternFlag = 0
vco2.DataLen = 8
vco2.Data = (0, 0, 0, 0, 0, 0, 0, 0)

ret = dll.VCI_OpenDevice(nDeviceType, nDeviceInd, nReserved)
print("opendevice:",ret)
ret = dll.VCI_SetReference(nDeviceType, nDeviceInd, nCANInd, 0, pointer(c_int(0x060003)))
print("setrefernce1:",ret)
ret = dll.VCI_SetReference(nDeviceType, nDeviceInd, 0, 0, pointer(c_int(0x060003)))
print("setrefernce0:",ret)  
ret = dll.VCI_InitCAN(nDeviceType, nDeviceInd, nCANInd, pointer(vic))
print("initcan0:",ret)


ret = dll.VCI_StartCAN(nDeviceType, nDeviceInd, nCANInd)
print("startcan0:",ret)

can_w=500
can_h=500
win_w=720
win_h=720

window=tk.Tk()
window.title('pan-tilt demo')
window.geometry('500x720')
label_1=tk.Label(window,text='Demo 1',bg='white',font=('Arial',10),width=30,height=1)
label_1.place(x=0,y=0)

cod_disp=tk.Canvas(window,bg='black',width=500,height=500)
cod_disp.place(x=0,y=180)

label_id=tk.Label(window,text='Object ID',bg='white',font=('Arial',10),width=30,height=1)
label_id.place(x=0,y=30)

defalut_id=tk.StringVar()
defalut_id.set('0')
id_sel=tk.Entry(window,font=('Arial',10),textvariable=defalut_id)
id_sel.place(x=250,y=30)

label_track_p=tk.Label(window,text='Pitch ',bg='white',font=('Arial',10),width=30,height=1)
label_track_p.place(x=0,y=60)

label_track_y=tk.Label(window,text='Yaw ',bg='white',font=('Arial',10),width=30,height=1)
label_track_y.place(x=250,y=60)

label_device=tk.Label(window,text='Device COM',bg='white',font=('Arial',10),width=30,height=1)
label_device.place(x=0,y=90)

_device_com_sel=tk.StringVar()
_device_com_sel.set('COM')
device_com_sel=tk.Entry(window,font=('Arial',10),textvariable=_device_com_sel)
device_com_sel.place(x=250,y=90)

device_conn=tk.Entry(window,font=('Arial',10))
device_conn.place(x=400,y=90)

label_rate=tk.Label(window,text='Baud Rate',bg='white',font=('Arial',10),width=30,height=1)
label_rate.place(x=0,y=120)

_device_rate=tk.StringVar()
_device_rate.set('115200')
device_rate=tk.Entry(window,font=('Arial',10),textvariable=_device_rate)
device_rate.place(x=250,y=120)

label_dis_h=tk.Label(window,text='Height Delta',bg='white',font=('Arial',10),width=30,height=1)
label_dis_h.place(x=0,y=150)

_delta_height=tk.StringVar()
_delta_height.set('0')
delta_height_sel=tk.Entry(window,font=('Arial',10),textvariable=_delta_height)
delta_height_sel.place(x=250,y=150)

device_connected=0

def main():

    object_info=[]
    object_arr=[]

    device_connected=0

    while 1:
        port=device_com_sel.get()
        state=device_conn.get()

        if device_connected==0 and port!='COM' and state!='':
            pan_device=serial.Serial(port, int(device_rate.get()))
            device_com_sel.config(bg='green')
            device_connected=1

        object_info=[]
        ret = dll.VCI_Receive(nDeviceType, nDeviceInd, 0, pointer(vco2), 1, 0)# receive

        if ret > 0:
            if vco2.ID==0x70b: #if filter cluster data
                print("*******************************************************")

                object_id=vco2.Data[0]

                dist_long_tmp_1=vco2.Data[1]
                dist_long_tmp_2=vco2.Data[2]
                dist_x=dist_long_tmp_1<<2 | dist_long_tmp_2>>6
                dist_x=dist_x*0.2-102

                dist_lat_tmp_1=vco2.Data[2]
                dist_lat_tmp_2=vco2.Data[3]
                dist_lat_tmp_1=dist_lat_tmp_1 & 0b00111111
                dist_y=dist_lat_tmp_1<<4 | dist_lat_tmp_2>>4
                dist_y=dist_y*0.2-102

                v_x_tmp_1=vco2.Data[3]
                v_x_tmp_2=vco2.Data[4]
                v_x_tmp_1=v_x_tmp_1 & 0b00001111
                v_x=v_x_tmp_1<<6 | v_x_tmp_2>>2
                v_x=v_x*0.25-128

                v_y_tmp_1=vco2.Data[4]
                v_y_tmp_2=vco2.Data[5]
                v_y_tmp_1=v_y_tmp_1 & 0b00000011
                v_y=v_y_tmp_1<<7 | v_y_tmp_2>>1
                v_y=v_y*0.25-64

                clu_state=vco2.Data[6]>>3

                clu_poss=vco2.Data[6] & 0b00000111

                object_rcs=vco2.Data[7]

                object_info=[object_id,dist_x,dist_y,v_x,v_y,clu_state,clu_poss,object_rcs]

                if object_id==0:
                    cod_disp.delete("all")  #refresh data

                exist_flag=0
                if(len(object_arr)>0):
                    for i in range(len(object_arr)):
                        if object_arr[i][0]==object_info[0]:
                            object_arr[i]=object_info
                            exist_flag=1

                if(exist_flag==0):
                    object_arr.append(object_info)

                print("object_id: ",object_id)
                print("object_X: ",dist_x)
                print("object_Y: ",dist_y)
                print("object_VX: ",v_x)
                print("object_VY: ",v_y)
                print("object_state: ",clu_state)
                print("object_poss: ",clu_poss)
                print("object_rcs: ",object_rcs)

                print("size overall arr: ",len(object_arr))
                print("*******************************************************")

                id_selected=id_sel.get()
                if(id_selected!=''):
                    id_selected=int(id_selected)

                #print(id_selected)
                clu_fill_color='blue'
                if(object_id==id_selected):
                    clu_fill_color='white'

                point_x=dist_y*2+can_w/2
                point_y=-1*dist_x*2+can_h
                cod_disp.create_oval(point_x-2.5,point_y-2.5,point_x+2.5,point_y+2.5,fill=clu_fill_color)
                cod_disp.create_line(point_x-4,point_y,point_x+4,point_y,fill='red')
                cod_disp.create_line(point_x,point_y-4,point_x,point_y+4,fill='red')
                cod_disp.create_text((point_x+7,point_y-7),text=str(object_id),font=('Arial',8),fill = 'white')
                window.update()

                for i in object_arr:
                    if i[0]==id_selected:
                        if(device_connected==1):
                            pitch_angle=math.atan(i[1]/(i[2]+0.0000001)) / math.pi *180
                            print("pitch angle: ",pitch_angle)

                            delta_height=0
                            if(delta_height_sel.get()!=''):
                                delta_height=float(delta_height_sel.get())

                            dist_target=math.sqrt(i[1]**2+i[2]**2)
                            yaw_angle=math.atan(delta_height/(dist_target+0.0000001)) / math.pi *180

                            label_track_p.config(text="Pitch "+str(pitch_angle))
                            label_track_y.config(text="Yaw "+str(yaw_angle))

                                    #云台串口
                            #print("Center of Rectangle is :", center)
                            data = "X{0:d}Y{1:d}Z".format(int(pitch_angle+90), int(-1*yaw_angle+90))
                            #print ("output = '" +data+ "'")
                            sdata = bytes(data, encoding = "utf8")
                            pan_device.write(sdata)


if __name__ == '__main__':
    main()