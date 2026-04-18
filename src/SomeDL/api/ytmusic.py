from ytmusicapi import YTMusic

import SomeDL.utils.console as console

# yt = YTMusic()


# General info:
# yt.get_song(video_id) Provides insufficient metadata (No artist, only uploader. No album info)


# === "wrapper" for ytmusicapi to cache get_album, as thats the only request that is very frequently redone (every time songs are from the same album)
class CachedYTMusic(YTMusic):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cache = {}

    def check_cache(self, ID):
        # === Check if in Cache ===
        if ID in self._cache:
            print(f"--- [CACHE HIT] {ID}")
            print(self._cache[ID]["artists"][0]["name"])
            return self._cache[ID]
        else:
            print("--- no cache")
            return None

    def add_to_cache(self, ID, data):
        # === Add to cache and return data again ===
        if len(self._cache) >= 100: # Number = Max size of cache
            # remove oldest item
            oldest_key = next(iter(self._cache))
            # print("removing:")
            # print(oldest_key)
            # print(self._cache[oldest_key].get("title"))
            del self._cache[oldest_key]
        
        
        # console.printj(self._cache)

        # --- remove unneccessary data
        if data.get("related_recommendations"):
            data.pop("related_recommendations")
        if data.get("other_versions"):
            data.pop("other_versions")
        
        if data.get("title"):
            # print("--- Add to cache")
            self._cache[ID] = data
        
        # print(len(self._cache))
        return data

    def get_album(self, browseId):
        # --- Currently the only thing that can reasonably be cached, as its refetched for every item if they are not donwloaded as a album directly
        result = self.check_cache(browseId)
        
        if result: 
            return result
        else:
            return self.add_to_cache(browseId, super().get_album(browseId))



yt = CachedYTMusic()






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