from moviepy import VideoFileClip, CompositeVideoClip

clip=(
    VideoFileClip("/Users/camilacastano/Desktop/cataracts1/gathering_info/p3-one.mp4")
    .subclipped(125,1500)
    .without_audio() 
)

final_clip=CompositeVideoClip([clip])
final_clip.write_videofile("p3_test")