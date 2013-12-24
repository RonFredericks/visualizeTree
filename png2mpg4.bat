@echo off
echo Batch File encodes a sequence of png files into mpeg-4 video using FFmpeg
:
REM File name: png2mpg4.bat
REM Ron Fredericks, LectureMaker LLC, http://www.LectureMaker.com
REM Revision 1 12/23/2013: Now auto-scales and supports HD video at 1920 x 1080 pixels
:
REM Files of the form: bst_graph00001.png, counting up.
REM Frame rate set to 1 seconds per frame on input and 12 fps on output.
REM Output video will reside in the same directory as the PNG sequence images.
REM Note the use of a double %% to encode sequence numbers in this batch file, 
REM      use only one % outside of the batch file.
:
REM ffmpg parameters used:
REM	-f image2 forces input to image file demuxer, creating video from many images, following a pattern
REM	-r 1 indicates reading input at 1 second for each png file
REM	-start_number 00001 is the start number for the png file sequence
REM	-i bst_graph%%05d.png is the input pattern for the png file image sequence (numbers are 5 digits long)
REM	-b:v 5000k is a high quality bitrate for video on output
REM	-vcodec mpeg4 is the video codec
REM	-r 30 is the frame rate for the video on output
REM	-vf scale=720:480 is a simple video filter to scale output to a normal size of 720x480
REM	-vf scale="'if(gt(a,4/3),1920,-1)':'if(gt(a,4/3),-1,1280)'" is a more advanced video filter to scale output to 1920x1080 (HD)
REM	-y overides output file without asking
REM	movie.mp4 is the output file name
:	
@echo on
cd .\vidImages
ffmpeg -f image2 -r 1 -start_number 00001 -i bst_graph%%05d.png  -b:v 5000k -vcodec mpeg4 -r 30 -vf scale="'if(gt(a,4/3),1920,-1)':'if(gt(a,4/3),-1,1280)'" -y movie.mp4
@echo off
:
ECHO.&ECHO.Press any key to end the application.&PAUSE>NUL&GOTO:EOF
