#!/usr/bin/python

import httplib
import base64
import StringIO
import threading
import time
import wx
import MWScore

import serial

servoTemperatures = [0]*18
dict_servoIndex = {11:1 , 12:2 , 13:3 , 14:4 , 21:5 , 22:6 , 23:7 , 24:8 , \
                   31:9 , 32:10 , 33:11 , 34:12 , 41:13 , 42:14 , 43:15 , 44:16, \
                      51:17 , 52:18 }
servoIDs = [11, 12, 13, 14, 21, 22, 23, 24, \
                   31, 32, 33, 34, 41, 42, 43, 44, \
                      51, 52]
                      
"""

    CONFIG STUFFS

"""

# Socket Client
SOCKET_CLIENT_HOST = "192.168.1.246"
SOCKET_CLIENT_PORT = 2525

# IP Camaera
CAMERA_IP = "192.168.1.70"
CAMERA_USERNAME = "admin"
CAMERA_PASSWORD = "admin"
CAMERA_SIZE_WIDTH = 620
CAMERA_SIZE_HEIGHT = 480
CAMERA_SIZE = (CAMERA_SIZE_WIDTH, CAMERA_SIZE_HEIGHT)

# HUD stuff
HUD_COLOR = wx.Color(0,255,0)

# Time
TIME_POSITION_X = 280
TIME_POSITION_Y = 20

# Scores
SCORE_POSITION_X = 20
SCORE_POSITION_Y1 = 50
SCORE_POSITION_Y2 = 70

# Crosshair
CROSSHAIR_POSITION_X = 310
CROSSHAIR_POSITION_Y = 240

"""

    Camera
    Note: Want to support other camera types in the future.

"""

class Camera():

    def __init__( self, ip, username, password ):
        self.IP = ip
        self.Username = username
        self.Password = password
        self.Connected = False
        
    def Connect( self ):
        pass
        
    def Disconnect( self ):
        pass
        
    def Update( self ):
        pass

class Trendnet( Camera ):

    def __init__( self, ip, username, password ):
        Camera.__init__( self, ip, username, password )
        
    def Connect( self ):
        if self.Connected == False:
            try:
                print "Attempting to connect to camera", self.IP, self.Username, self.Password
                h = httplib.HTTP( self.IP )
                h.putrequest( "GET", "/cgi/mjpg/mjpeg.cgi" )
                h.putheader( "Authorization", "Basic %s" % base64.encodestring( "%s:%s" % (self.Username, self.Password))[:-1] )
                h.endheaders()
                errcode, ermsg, headers = h.getreply()
                self.File = h.getfile()
                print "Connected!"
                self.Connected = True
            except:
                print "Unable to connect!"
                self.Connected = False
        
    def Disconnect( self ):
        self.Connected = False
        print "Camear Disconnected!"
        
    def Update( self ):
        if self.Connected:
            s = self.File.readline() # "--myboundry'
            s = self.File.readline() # "Content-Length: #####"
            framesize = int(s[16:])
            s = self.File.read( framesize ) # jpeg data
            while s[0] != chr(0xff):
                s = s[1:]
            return StringIO.StringIO(s)

class DLink( Camera ):

    def __init__( self, ip, username, password ):
        Camera.__init__( self, ip, username, password )
        pass
        
    def Connect( self ):
        pass
        
    def Disconnect( self ):
        pass
        
    def Update( self ):
        pass

"""

    CameraPanel
    
"""

class CameraPanel( wx.Panel ):

    def __init__( self, parent, camera, socketclient ):
        wx.Panel.__init__( self, parent, id=wx.ID_ANY, style=wx.SIMPLE_BORDER )
        
        self.Camera = camera
        self.SocketClient = socketclient
        
        self.Bind( wx.EVT_PAINT, self.OnPaint )
        self.Bind( wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground )
        
        self.AButton = wx.Button(self, label="Unused button",pos=(950,460))
        
        self.SetSize( CAMERA_SIZE )
        
        
        self.leftcolor  = wx.BLUE_BRUSH
        self.rightcolor = wx.BLUE_BRUSH
        
    def OnEraseBackground( self, event ):
        pass
        
    def OnPaint( self, event ):
        
        dc = wx.BufferedPaintDC( self )
        
        # Draw the camera image
        if self.Camera.Connected:
            try:
                stream = self.Camera.Update()
                if stream != None:
                    img = wx.ImageFromStream( stream )
                    bmp = wx.BitmapFromImage( img )
                    dc.DrawBitmap( bmp, 150, 0, True )
            except:
                pass
        
        # If camera not connected draw blank white screen
        else:
            dc.SetBrush( wx.WHITE_BRUSH )
            dc.DrawRectangle( -1, -1, CAMERA_SIZE_WIDTH, CAMERA_SIZE_HEIGHT )
            
        # Draw the SocketClient match data
        # print 'xxx'
        #if self.SocketClient.Thread.isAlive():
            #print 'alive'
        
        if self.SocketClient != None:
            dc.SetTextForeground( HUD_COLOR )
            
            # Clock
            min = self.SocketClient.MatchTime / 600
            sec = int((self.SocketClient.MatchTime -(min * 600)) * .1)
            
            dc.DrawText( str(min).rjust(2, "0") + ":" + str(sec).rjust(2, "0"), TIME_POSITION_X, TIME_POSITION_Y )
            
            dc.SetBrush(wx.BLACK_BRUSH)
            dc.DrawRectangle(0, 0, 150, 400)
            # Scores
            for m in xrange(self.SocketClient.NumMechs):
                dc.DrawText( self.SocketClient.MechNames[m], SCORE_POSITION_X, SCORE_POSITION_Y1+(40*m) )
                dc.DrawText( str(self.SocketClient.MechHP[m]), SCORE_POSITION_X, SCORE_POSITION_Y2+(40*m) )
            
        # Draw the crosshairs

        dc.SetBrush(wx.BLACK_BRUSH)        
        dc.DrawRectangle(800, 40, 200, 400)
        
        dc.SetBrush(self.leftcolor)
        dc.DrawRectangle(140, 40, 20, 400) # x, y, xextent, yexten
        dc.SetBrush(self.rightcolor)
        dc.DrawRectangle(780, 40, 20, 400)
        
        for i in xrange(18):
            dc.DrawText("Servo {0}     T: {1}".format(servoIDs[i], \
                                            servoTemperatures[i]),815,60+i*20)
        
        # If xbee serial port was opened and is open.
        if serExist and ser.isOpen():
            # read all bytes in the buffer
            while ser.inWaiting():
                byte = ser.read()
                # if the end of packet symbol is seen...
                if byte == ')':
                    dataType = byte_string.split()[0][0]
                    try:
                        # print "hi"
                        #int(num)
                      #  print num, dataType
                        if dataType == 'R':
                            num = byte_string.split()[0][2:]
                            if int(num) < 21:
                                campanel.rightcolor = wx.RED_BRUSH
                            elif int(num) < 26:
                                campanel.rightcolor = wx.Brush(wx.Color(255,153,51))
                            elif int(num) < 35:
                                campanel.rightcolor = wx.Brush(wx.Color(255,255,51))
                            else:
                                campanel.rightcolor = wx.GREEN_BRUSH
                        elif dataType =='L':
                            num = byte_string.split()[0][2:]
                            if int(num) < 19:
                                campanel.leftcolor = wx.RED_BRUSH
                            elif int(num) < 26:
                                campanel.leftcolor = wx.Brush(wx.Color(255,153,51))
                            elif int(num) < 35:
                                campanel.leftcolor = wx.Brush(wx.Color(255,255,51))
                            else:
                                campanel.leftcolor = wx.GREEN_BRUSH
                        elif dataType == 'S':
                            print byte_string
                            num = byte_string.split()[0][2:]
                            servoIndex = dict_servoIndex[int(num)] - 1
                            # print int(num)
                        elif dataType == 'T':
                            num = byte_string.split()[0][2:]
                            servoTemperatures[servoIndex] = int(num)
                    except ValueError, error:
                        print error
                    finally:
                        byte_string = ""
                        break
                else:
                    byte_string = byte_string + byte
                    
            if arbcomserExist and arbcomser.isOpen():    
                while arbcomser.inWaiting():
                    # forwarding bytes
                    byte = arbcomser.read()
                    ser.write(byte)
        
"""

    MWCam
    
"""
        
class MWCam( wx.Frame ):

    ID_FRAME_REFRESH = wx.NewId()

    def __init__( self ):
        wx.Frame.__init__( self, None, wx.ID_ANY, "MWCam", style=wx.DEFAULT_FRAME_STYLE & ~wx.RESIZE_BORDER )
        
        # Socket Cleint
        self.SocketClient = MWScore.SocketClient( SOCKET_CLIENT_HOST, SOCKET_CLIENT_PORT )
        self.SocketClient.StartThread()
        
        # IP Camera
        self.Camera = Trendnet( CAMERA_IP, CAMERA_USERNAME, CAMERA_PASSWORD )
        self.Camera.Connect()
        
        # Camera Panel
        self.CameraPanel = CameraPanel( self, self.Camera, self.SocketClient )
        
        # Frame timer
        self.Timer = wx.Timer( self, self.ID_FRAME_REFRESH )
        self.Timer.Start(10)
        wx.EVT_TIMER( self, self.ID_FRAME_REFRESH, self.Refresh )
        
        # Frame Sizer
        self.Sizer = None
        self.Size()
        
        # Show frame
        self.Show( True )
        
    def Size( self ):
        self.Sizer = wx.BoxSizer( wx.VERTICAL )
        self.Sizer.Add( self.CameraPanel, 1, wx.EXPAND|wx.ALL, 5 )
        self.SetSizer( self.Sizer )
        self.Fit()
        
    def Refresh( self, event ):
        self.CameraPanel.Refresh()

if __name__ == "__main__":
    # xBee serial port settings
    myPort = 14 #15 #~ note: use port number - 1
    # myPort = 16 #15 #~ note: use port number - 1
    myBaud = 38400
    
    # Arbotix Commander serial port settings
    myPort2 = 11 #12 #~ note: use port number - 1
    myBaud2 = 38400
    
    app = wx.App(0)
    
    # Supress crazy erorr boxes
    wx.Log_SetActiveTarget( wx.LogStderr() )
    
    # Opening the serial port for the xBee
    try:
        ser = serial.Serial(myPort,myBaud) #port number - 1
        print "Successfully connected to port {0} at {1} baud".format(myPort,myBaud)
        serExist = 1
    
    except serial.SerialException:
        print "Couldn't open xBee serial port. Try again later."
        serExist = 0
    
    # Opening the serial port for the Arbotix Commander
    try:
        arbcomser = serial.Serial(myPort2,myBaud2) #port number - 1
        print "Successfully connected to port {0} at {1} baud".format(myPort2,myBaud2)
        arbcomserExist = 1
    
    except serial.SerialException:
        print "Couldn't open Arbotix Commander serial port. Try again later."
        arbcomserExist = 0
    
    frame = MWCam()
    app.MainLoop()

