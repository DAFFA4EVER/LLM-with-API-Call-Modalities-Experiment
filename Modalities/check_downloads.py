def check_downloads():
    import os

    # Opens the Downloads folder
    os.system('explorer %userprofile%\Downloads')

    return "Opening Downloads Folder"