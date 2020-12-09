import music_tag
f = music_tag.load_file('/Volumes/nathanbackup/Downloads/CDA68266 - Mantyjarvi - Choral Music - 2020/2. Stuttgarter Psalmen - 1. Warum toben die Heiden?.m4a')
f['tracknumber'] = 3
f['totaltracks'] = 12
f.save()
