"""
File: slideShow.py

 Support Module for: Animate a Binary Search Tree using Python, and TK graphics

 Project home: http://www.embeddedcomponents.com/blogs/2013/12/visualizing-software-tree-structures/
 
 Developed by Ron Fredericks, Video Technologist, at LectureMaker LLC, http://www.LectureMaker.com
    MIT License, Copyright (c) 2013, Ron Fredericks
    Free to use following these terms: http://opensource.org/licenses/MIT  


 
################################################
# Class slideShow
################################################

Animate a sequence of images in a TK window, assumes all images are the same size.                          

Public methods: 
    slideShow(rootTk)  - instantiate slide show class
    setImageScaling()  - update default image scale factor
    setSpeedList()     - update default list of playback speeds
    setColorScheme()   - update default button color scheme
    setIdleTimeSlice() - update defalut sleep time during idle loop
    playSlides()       - launch a slide show   
"""

# Import TK graphics packages.
import Tkinter 
import Image, ImageTk

import time

# History:
#   Initial project published on 12/11/2013
#
#   Rev 1: 12/16/2013
#       1) Improve comments for accuracy.
#
#   Rev 2: 12/23/2013
#       1) Improve comments for accuracy.
#
#   Rev 3: 1/4/2014
#       1) Create (this) slideShow.py module to clarify and shorten original project code.
#       2) Turn single image display into slideShow() class to display multiple images.
#   Rev 3a: 1/10/2014
#       1) Improve clarity of idle loop
#       2) Improve clarity of performance display in main playback loop


class slideShow(object):
    def __init__(self, rootTk):
        
        # Root for TK graphics (example: rootTk = Tkinter.Tk())
        self.rootTk = rootTk
        # Text title for TK graphics playback window.
        self.mainTitle = "Slide Show"
        # List of images to play during slide show (example: playList = ["c:\tmp\im1.png", "c:\tmp\im2.png"...]).
        self.playList = []
        # Activate (set True) to display performance of main timing loop to screen (standard output).
        self.testPerformance = False        
               
        # Polling loop controls for playSlides() method...          
        self.speedList = [.01, .05, .1, .35, .5, 1., 2.]  # A sorted list of wait times between images to play during a slide show,
                                                          #   where speedList pointer controlled by "Faster" and "Slower" buttons.
        self.speedPointerDefault = 3                      # The default wait time (during startup and after a reset) index within speedList[]. 
                                                          #   Recommended setting (integer): len(speedList)/2
        self.idleTimeSlice = .01/2.1                      # Idle loop time slice between Tkinter updates. 
                                                          #   Recommend setting based on Nyquist Interval (float): min(.1, speedList[0]/2.1),
                                                          #   and the need for python code associated with button activity to be responsive to user.
        
        # Button colors...
        self.bg_color_f = "#ccffff"  # Background color for buttons.
        self.bg_color_r = "#ffffcc"  # Background color for play/pause button and reverse/normal buttons
                                     #    when user selects reverse playback option.
        self.fg_color_f = "blue"     # Text color for buttons.
        self.fg_color_r = "black"    # Text color for play/pause button and reverse/normal buttons
                                     #    when user selects reverse playback option.                                     
        self.exitButtonText = "Quit" # Text for use in exit button, use "Next" (for example), 
                                     #    when cascading several slide shows together. 
                                     
        # Image scaling to fit within monitor...
        self.w_screen = None         # Width of screen: use None for auto-detection and auto-scaling, 
                                     #   otherwise set to maximum png width in pixels plus 20 for borders (controller width only takes 420).
        self.h_screen = None         # Height of screen: use None for auto-detection and auto-scaling, 
                                     #   otherwise set to maximum png height in pixels plus 70 for borders, title bar, and buttons (controller height only takes 66).                
        
    def setImageScaling(self, wMax, hMax):
        # Set maximum width and height values in pixels for png images. 
        #    Auto-scaling will take place when images are larger than these values.
        self.w_screen = float(wMax)
        self.h_screen = float(hMax)
        
    def setSpeedList(self, speedList, speedPointerDefault):
        # Update the default list of playback times offered by the "faster" / "slower" buttons
        assert len(speedList) >= 3, "List should be 3 or floating point times. Example: speedList = [.01, .05, .1, .35, .5, 1., 2.]"
        assert speedPointerDefault < len(speedList), "Default time pointer should be an integer: between 0 and len(speedList) - 1" 
        self.speedList = speedList        
        self.speedPointerDefault = speedPointerDefault   
        
    def setIdleTimeSlice(self, idleTimeSlice):
        # Update the default idle loop time slice. Use faster time for more responsive buttons. Use slower time for slower computers.
        assert type(idleTimeSlice) == float, "Wait time between rootTk.update() calls should be a float. Example: idleTimeSlice = .05"
        self.idleTimeSlice = idleTimeSlice   
        
    def setColorScheme(self, bg_color_f="#ccffff", bg_color_r="#ffffcc", fg_color_f="blue", fg_color_r="black"):  
        # Set text and background colors for buttons. The "_f" colors are used for initial buttons, and controller title. 
        #    The "_r" colors are used for revere playback on "play/pause" and "normal" buttons.
        self.bg_color_f = bg_color_f
        self.bg_color_r = bg_color_r                                     
        self.fg_color_f = fg_color_f    
        self.fg_color_r = fg_color_r   
                                                                                                                                                                                                                                                                                                                                           
   
    def setExitFlag(self):
        # Exit play loop when user clicks operating system's window exit button, or slideShow's "Quit" button.
        # manage WM_DELETE_WINDOW event
        self.closeViewer = True
        self.measureValid = False
        
    def tooglePlayPause(self):
        # Modify play loop for playback or pause. Auto pause when playback comes to an end.
        self.measureValid = False
        if self.playFlag:
            self.Play.configure(text = ' Play  ')
            self.playFlag = False
        elif not self.playFlag and not self.reverseFlag and self.imageCount < self.imageCountMax:
            # forward play should only take place when imageCount (frame count) is not already at the end
            self.Play.configure(text = 'Pause')
            self.playFlag = True
        elif not self.playFlag and self.reverseFlag and self.imageCount > 0:
            # reverse play should only take place when imageCount (frame count) is not already at the begining
            self.Play.configure(text = 'Pause')
            self.playFlag = True   
        else:
            # Auto pause when playback comes to an end.
            self.toogleReverse()
             
    def incrementFaster(self):
        # Modify play loop for shorter delay between images.   
        self.speedPointerCurrent = max(0, self.speedPointerCurrent-1)      
        self.setTime = self.speedList[self.speedPointerCurrent] 
        self.updateSpeedButtons()
       
    def incrementSlower(self):
        # Modify play loop for longer delay between images.
        self.speedPointerCurrent = min(len(self.speedList)-1, self.speedPointerCurrent+1)      
        self.setTime = self.speedList[self.speedPointerCurrent] 
        self.updateSpeedButtons()

    def updateSpeedButtons(self):
        # Helper function for "faster" and "slower" buttons to display correct text with each button.
        self.measureValid = False
        tmpText = '{:7.2f}'.format(self.setTime)
        if self.testPerformance == True:
            print "Update time:", tmpText          
        self.Speed.configure(text = tmpText)
        if self.speedPointerCurrent == len(self.speedList)-1:
            self.Slower.configure(text = 'Slowest') 
        else:
            self.Slower.configure(text = 'Slower')    
        if self.speedPointerCurrent == 0:
            self.Faster.configure(text = 'Fastest') 
        else:
            self.Faster.configure(text = 'Faster')     
         
    def toogleReverse(self):
        # Modify play loop for forward or reverse playback. 
        #    Update play/pause and reverse/normal button color scheme for improved user awareness of current state.
        self.measureValid = False
        if self.reverseFlag:
            self.reverseFlag = False
            self.Reverse.configure(text = 'Reverse', bg=self.bg_color_f, fg=self.fg_color_f) 
            self.Play.configure(bg=self.bg_color_f, fg=self.fg_color_f)
        else:
            self.reverseFlag = True 
            self.Reverse.configure(text = 'Normal', bg=self.bg_color_r, fg=self.fg_color_r)
            self.Play.configure(bg=self.bg_color_r, fg=self.fg_color_r)
    
    def doReset(self):
        # Modify play loop to initial state.
        self.measureValid = False  
        self.resetJustHappened = True 
        self.setTime = self.speedList[self.speedPointerDefault]  
        self.speedPointerCurrent = self.speedPointerDefault
        self.updateSpeedButtons()
        if self.reverseFlag:
            self.toogleReverse()
        if self.playFlag:   
            self.tooglePlayPause()
        if self.imageCount != 0:  
            self.imageCount = 0

    def scaleFactor(self):        
        # Determine visual environment, and generate width/height scale dimensions as needed.
        # Output: Return tuple: updated width and height, and flag to scale or not.
        
        # Get screen size. Leave some room for boarders and buttons, use float values for scale calculations.
        if not self.w_screen:
            self.w_screen = self.rootTk.winfo_screenwidth() - 20
            
        if not self.h_screen:
            self.h_screen = self.rootTk.winfo_screenheight() - 70
        # Get width, height, and then initialize display using initial png image in sequence
        image = Image.open(self.playList[0])
        w = image.size[0]
        h = image.size[1]
        
        scaleFactorW = 1.
        scaleFactorH = 1.
        if w > self.w_screen:
            scaleFactorW = w / self.w_screen
        if h > self.h_screen:
            scaleFactorH = h / self.h_screen
            
        # Find largest scale factor, a scale factor below 1.0 would cause image to be magnified.
        scaleFactor = max(1. , max(scaleFactorW, scaleFactorH))
        w = int(w / scaleFactor)
        h = int(h / scaleFactor)
        
        # Determine if scaling should be done on images.
        useScaleFactor = False
        if scaleFactor != 1.:
            useScaleFactor = True 
        
        #Return tuple: updated width and height, and flag to scale or not.
        return (w, h, useScaleFactor)    
 
        
    def playSlides(self, playList, mainTitle="Slide Show", exitButtonText="Quit", testPerformance=False):
        # Main playback loop
        
        self.initPrivateProps() 
          
        assert len(playList) > 0, 'Error: playList is a ist of images to play during slide show (example: playList = ["c:\tmp\im1.png", "c:\tmp\im2.png"...])' 
        self.playList = playList
        
        self.mainTitle = mainTitle
        
        assert type(exitButtonText) == str, "Error: Exit button text should be passed as a string value"
        self.exitButtonText = exitButtonText
        
        self.testPerformance= testPerformance        
        
        assert self.rootTk and self.rootTk.winfo_exists(), "Error: Tkinter root not valid (initialization example: s = slideShow(Tkinter.Tk(), 'Title')"
        
        self.rootTk.title(self.mainTitle)                           # Place title in top window boarder.
        self.speedPointerCurrent = self.speedPointerDefault         # Current playback speed set to default time index in speedList[].
        self.setTime = self.speedList[self.speedPointerCurrent]     # Initialize time to wait between images during playback.
        self.imageCountMax = len(self.playList) - 1                 # Maximum image count [0 to n].                
        
        wScale, hScale, useScale = self.scaleFactor()               # Calculate image scale details
              
        # group buttons together tightly using this frame
        frame = Tkinter.Frame(self.rootTk, width=100)
        frame.grid(row = 1, column=1)
        
        # manage user buttons
        #---------------------
        
        # place menu name by the buttons
        msg = Tkinter.Label(frame, text="Controller: ", font=("Helvetica", 14), fg=self.fg_color_f)
        msg.grid(row = 1, column = 0)
        
        # define play/pause button
        self.Play = Tkinter.Button(frame, text = " Play  ", bg=self.bg_color_f, fg=self.fg_color_f, command = self.tooglePlayPause)
        self.Play.grid(row = 1, column = 1)
        
        # define play faster and slower buttons
        self.Faster = Tkinter.Button(frame, text = "Faster", bg=self.bg_color_f, fg=self.fg_color_f, command = self.incrementFaster, width=6)
        self.Faster.grid(row = 1, column = 2)
        self.Speed = Tkinter.Label(frame, text = '{:7.2f}'.format(self.setTime), fg=self.fg_color_f, relief="sunken", borderwidth=2)
        self.Speed.grid(row = 1, column = 3)
        self.Slower = Tkinter.Button(frame, text = "Slower", bg=self.bg_color_f, fg=self.fg_color_f, command = self.incrementSlower, width=6)
        self.Slower.grid(row = 1, column = 4)
        
        # define reverse play button
        self.Reverse = Tkinter.Button(frame, text = "Reverse", bg=self.bg_color_f, fg=self.fg_color_f, command = self.toogleReverse)
        self.Reverse.grid(row = 1, column = 5)
        
        # define reset button
        Reset = Tkinter.Button(frame, text = "Reset", bg=self.bg_color_f, fg=self.fg_color_f, command = self.doReset)
        Reset.grid(row = 1, column = 6)
        
        # define quit button, and link window exit button to it
        self.rootTk.protocol("WM_DELETE_WINDOW", self.setExitFlag)
        Exit = Tkinter.Button(frame, text = self.exitButtonText, bg=self.bg_color_f, fg=self.fg_color_f, command = self.setExitFlag)
        Exit.grid(row = 1, column = 7)
              
        # Initialize main polling loop.
        self.doReset()
        self.resetJustHappened = False   
        startMeasureTime = 0.  # measureValid will is initialized to False during doReset()
        
        # Main polling loop.
        while True:          
            if self.testPerformance == True:
                if self.measureValid:
                    deltaTime = time.clock() - startMeasureTime
                    print "deltaTime:", '{:2.5f}'.format(deltaTime), "imageCount:", "%02d" % (self.imageCount)                  
                startMeasureTime = time.clock()
                self.measureValid = True
            
            # Exit slide show if a quit button or exit window button was pressed.
            if self.closeViewer:
                break
                        
            # Display an image.
            f = self.playList[self.imageCount]
            image = Image.open(f)
            if useScale: image = image.resize((wScale,hScale),Image.ANTIALIAS) 
            # Use alternate image storage to avoid flicker.
            if self.imageCount % 2 == 0:
                tkpi = ImageTk.PhotoImage(image)        
                label_image = Tkinter.Label(self.rootTk, image=tkpi, relief="sunken")
                label_image.grid(row=0, columnspan=6)              
            else:
                tkpi2 = ImageTk.PhotoImage(image)        
                label_image2 = Tkinter.Label(self.rootTk, image=tkpi2, relief="sunken")
                label_image2.grid(row=0, columnspan=6)
            self.rootTk.update()             
            
            # Initialize wait time.        
            idleLoopTimeInit = time.clock() 
            while True:
                # Idle polling loop. Wait for user controls, ellapsed time to next image, or end of slide show.
                
                # update TK graphics thread.
                self.rootTk.update()
                
                # Exit idle loop on quit/close
                if self.closeViewer:
                    break              
                # Exit idle loop on reset
                if self.resetJustHappened:
                    break
                    
                # Skip idle loop on initial image.
                if self.playFlag:
                    if self.imageCount == 0 and not self.reverseFlag:
                        self.measureValid = False
                        break
                    elif self.imageCount == self.imageCountMax and self.reverseFlag:
                        self.measureValid = False
                        break
                    else: 
                        if time.clock() - idleLoopTimeInit > self.setTime:
                            # Re-initialize wait time unless playback is underway.        
                            idleLoopTimeInit = time.clock()
                            break
                        # Update graphics display at least every idleTimeSlice seconds, even when we want to delay for a longer period of time.                                     
                        time.sleep(self.idleTimeSlice)                                                      
                
            if self.imageCount >= self.imageCountMax and not self.reverseFlag:
                # Stop normal playback, update play/pause button text, and wait in a loop.
                self.tooglePlayPause()
                # Toogle reverse playback so the user can play the png images in reverse direction.
                self.toogleReverse()
            
            elif self.imageCount <= 0 and self.reverseFlag:
                # Stop reverse playback, update play/pause button text, and wait in a loop.
                self.tooglePlayPause()
                # Toogle reverse playback so the user can play the png images in forward direction.
                self.toogleReverse()
                            
            elif not self.resetJustHappened:
                # Normal playback by incrementing/decrementing the png image to display.
                if self.reverseFlag:
                    self.imageCount -= 1
                else:
                    self.imageCount += 1
            else:
                # clear reset flag and return to main playback loop with all attributes reset
                self.resetJustHappened = False                    
        
    def initPrivateProps(self):                             
        # Private attributes for play loop and interactive button management.                             
        self.closeViewer = False
        self.playFlag = False
        self.Play = None
        self.Reverse = None
        self.reverseFlag = False
        self.imageCount = 0        
        self.measureValid = False
        self.Speed = None
        self.Faster = None
        self.Slower = None
        self.resetJustHappened = False 
