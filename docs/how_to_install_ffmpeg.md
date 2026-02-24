# Quick guide on how to install python on Linux
FFmpeg should be available on all linux distros via the package manager. Example:
### Arch Linux
```
pacman -S ffmpeg
```
### Debian, Ubuntu and all distros that use apt
```
sudo apt install ffmpeg
```
### Fedora
```
sudo dnf install ffmpeg
```
### OpenSuse
```
sudo zypper install ffmpeg
```


# Quick guide on how to install ffmpeg on Windows
You can either install ffmpeg via [winget](https://www.gyan.dev/ffmpeg/builds/), or follow this instruction for a manual install:


- Go to the ffmpeg website: https://ffmpeg.org/download.html
- Click on "Windows builds by BtbN".

![Windows builds by BtbN](images/ffmpeg/1_ffmpeg_site.png)

- From github, download newest windows build.

![Windows builds](images/ffmpeg/2_github.png)

- Extract the contents to a path of your liking, for example `C:\ffmpeg`.

![3_extract_all](images/ffmpeg/3_extract_all.png)

![4_dest_folder](images/ffmpeg/4_dest_folder.png)

- Go into the extracted folder and locate the `bin` folder.
- Copy the folder path

![5_copy_folder_name](images/ffmpeg/5_copy_folder_name.png)

- Now you have to add this folder to path:
- Type "environment variables" in the search, open "Edit the system environment variables"

![6_search_environment](images/ffmpeg/6_search_environment.png)

- In there, at the bottom click "Environment Variables..."

![7_env_var](images/ffmpeg/7_env_var.png)

- Click on "Path" and then "Edit"

![8_edit_path](images/ffmpeg/8_edit_path.png)

- Click "New" and then paste the path of the bin folder in there

![9_paste_path](images/ffmpeg/9_paste_path.png)

- Click OK on all windows
- Reopen all CMD or PowerShell windows
