
# Downsize video to reduce file size and improve upload onto Labelbox (manual for now)

# Use of FFmpeg to downsize video files. This script will take a video file as input and output a downsized version of the video.
# We used it before, can be useful now:

from moviepy import *

def resize_video(input_path,
                 output_path,
                 width,
                 height):
    video=VideoFileClip(input_path)
    resized_video=video.resized((width, height))
    resized_video.write_videofile(output_path,
                                  fps=30,
                                  codec='libx264',
                                  audio_codec='aac')
    video.close()

input_file=r'/Users/camilacastano/Desktop/cataracts_initial/first_test_phaco_p3.mp4'
output_file=r'/Users/camilacastano/Desktop/cataracts_initial/first_test_phaco_p3_downsized.mp4'
desired_width=840
desired_height=420

resize_video(input_file,output_file,desired_width,desired_height)