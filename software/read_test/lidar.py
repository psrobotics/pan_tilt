
#python3.8.0 64位（python 32位要用32位的DLL）
#
from ctypes import *
 
VCI_USBCAN2 = 4
STATUS_OK = 1
class VCI_INIT_CONFIG(Structure):  
    _fields_ = [("AccCode", c_uint),
                ("AccMask", c_uint),
                ("Reserved", c_uint),
                ("Filter", c_ubyte),
                ("Timing0", c_ubyte),
                ("Timing1", c_ubyte),
                ("Mode", c_ubyte)
                ]  
class VCI_CAN_OBJ(Structure):  
    _fields_ = [("ID", c_uint),
                ("TimeStamp", c_uint),
                ("TimeFlag", c_ubyte),
                ("SendType", c_ubyte),
                ("RemoteFlag", c_ubyte),
                ("ExternFlag", c_ubyte),
                ("DataLen", c_ubyte),
                ("Data", c_ubyte*8),
                ("Reserved", c_ubyte*3)
                ] 
 
CanDLLName = './ControlCAN.dll' #把DLL放到对应的目录下
canDLL = windll.LoadLibrary('./ControlCAN.dll')
#Linux系统下使用下面语句，编译命令：python3 python3.8.0.py
#canDLL = cdll.LoadLibrary('./libcontrolcan.so')


print(CanDLLName)
 
ret = canDLL.VCI_OpenDevice(VCI_USBCAN2, 0, 0)
if ret == STATUS_OK:
    print('调用 VCI_OpenDevice成功\r\n')
if ret != STATUS_OK:
    print('调用 VCI_OpenDevice出错\r\n')
 
#初始0通道
vci_initconfig = VCI_INIT_CONFIG(0x80000000, 0xFFFFFFFF, 0,
                                 0, 0x00, 0x1c, 0)#波特率500k，正常模式
ret = canDLL.VCI_InitCAN(VCI_USBCAN2, 0, 0, byref(vci_initconfig))#device name, unknown, port, config
if ret == STATUS_OK:
    print('调用 VCI_InitCAN1成功\r\n')
if ret != STATUS_OK:
    print('调用 VCI_InitCAN1出错\r\n')
 
ret = canDLL.VCI_StartCAN(VCI_USBCAN2, 0, 0)
if ret == STATUS_OK:
    print('调用 VCI_StartCAN1成功\r\n')
if ret != STATUS_OK:
    print('调用 VCI_StartCAN1出错\r\n')

ubyte_array = c_ubyte*8
ubyte_3array = c_ubyte*3
a = ubyte_array(0, 0, 0, 0, 0, 0, 0, 0)
b = ubyte_3array(0, 0 , 0)
#通道2接收数据

vci_can_obj = VCI_CAN_OBJ(0x0, 0, 0, 0, 0, 0,  0, a, b)#复位接收缓存
ret = canDLL.VCI_Receive(VCI_USBCAN2, 0, 0, byref(vci_can_obj), 2500, 0)
#print(ret)
while 1:#如果没有接收到数据，一直循环查询接收。
    ret = canDLL.VCI_Receive(VCI_USBCAN2, 0, 0, byref(vci_can_obj), 2500, 0)
    if vci_can_obj.ID>0:#接收到一帧数据
        print('CAN1通道接收成功\r\n')
        print('ID：')
        print(vci_can_obj.ID)
        print('DataLen：')
        print(vci_can_obj.DataLen)
        print('Data：')
        #print(list(vci_can_obj.Data))
 
#关闭
canDLL.VCI_CloseDevice(VCI_USBCAN2, 0) 

