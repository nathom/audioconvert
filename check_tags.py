import audioconvert

dir = '/Volumes/nathanbackup/Downloads'
f = audioconvert.find('wav', 'flac', 'm4a', dir=dir)
print(f)
