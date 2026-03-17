from ytmusicapi import YTMusic
from SomeDL.utils.logging import printj, timerstart, timerend

yt = YTMusic()



# timerstart("YT")

# artist_res = yt.search("delain", filter="artists")


# printj(artist_res)


# exit()

# artist_info = yt.get_artist("UCijF534Q4VFffUT-B4TFT9Q")
# artist_info = yt.get_artist("UCPIXyGsEUrGIz7olJ1d7-Ig")
# artist_info = yt.get_album("MPREb_EtNdKFDvyZV")

# printj(artist_info)

# pl = yt.get_playlist("PLenYtP8i7iO0MgYwm9H3jZFML989XvLnP", limit=None)

# printj(pl)

# https://music.youtube.com/playlist?list=PLcb1ZAWRDY7XtwMJ-Dw82WC0VgTDsRtBH

# print(len(pl["tracks"]))


# timerend("YT")



# from requests.exceptions import ConnectionError

# try:
#     result = yt.search("Delain - we are the others")
#     print("success!")
# except ConnectionError:
#     print("No connection - retry later")
