from ytmusicapi import YTMusic

import SomeDL.utils.console as console

yt = YTMusic()

"""
General info:
yt.get_song(video_id) Provides insufficient metadata (No artist, only uploader. No album info)

"""




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



# mement = yt.get_playlist("OLAK5uy_kVJo6ExGxz5Phm6RN2FTjBfhMGAB6MwWI", limit=None)
# mement = yt.get_album("MPREb_9BXkH6guf4N")
# printj(mement)


# https://music.youtube.com/browse/MPREb_9BXkH6guf4N


# https://music.youtube.com/browse/MPREb_B9YcEZY20ip



# mement = yt.get_playlist("OLAK5uy_nHlwZujC7fzEgTnKdakqBzO7MIP9sZW48", limit=None)
# mement = yt.get_album("MPREb_B9YcEZY20ip")
# mement = yt.get_album("MPREb_Sq9DdOEdRQz")
# console.printj(mement)


# omv = yt.get_song("NoH6WYXpCXw")
# printj(omv)
#

# intr = yt.get_watch_playlist("Q9hEA4U7tGM", limit=1)
# printj(intr)


# search_results_query = yt.search("delain - dance with the devil", filter="songs")

# printj(search_results_query)