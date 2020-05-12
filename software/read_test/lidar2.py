from ctypes import *

dll = windll.LoadLibrary('./ControlCAN.dll')
nDeviceType = 4 #* USBCAN-2E-U *
nDeviceInd = 0#* 索引号0 *
nReserved = 0
nCANInd = 0 #can通道号

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
print("setrefernce0:",ret)  #注意，SetRefernce必须在InitCan之前
ret = dll.VCI_InitCAN(nDeviceType, nDeviceInd, nCANInd, pointer(vic))
print("initcan0:",ret)
#ret = dll.VCI_InitCAN(nDeviceType, nDeviceInd, 0, pointer(vic))
#print("initcan0:",ret)

ret = dll.VCI_StartCAN(nDeviceType, nDeviceInd, nCANInd)
print("startcan0:",ret)
#ret = dll.VCI_StartCAN(nDeviceType, nDeviceInd, 0)
#print("startcan0:",ret)
while 1:
    #ret = dll.VCI_Transmit(nDeviceType, nDeviceInd, nCANInd, pointer(vco), 1)# 发送两帧
    #print("transmit:",ret)
    ret = dll.VCI_Receive(nDeviceType, nDeviceInd, 0, pointer(vco2), 1, 0)# 发送两帧
    #print("receive:",ret)
    if ret > 0:
        print(vco2.ID)
        print(vco2.DataLen)
        print(list(vco2.Data))

