## :notebook_with_decorative_cover: &nbsp;Info:

This is a python script to turn facebook messages into pdfs, from back in 2021. It uses python 3.9.5 and python module fpdft 2.4.2
So versions lower than these might have some problems. Also it uses json files downloaded from Facebook. From facebook one can easily download their user info, message history, and even the photos, videos, audios shared through messages. After downloading the json version of facebook info, this script should be able to work properly.

## Steps:

1. First you need to download message information form facebook.
From facebook, go to Your information and permissions from settings.
Then you can find Download your information. From there you can choose to download your message informations.
Make sure at the final step you select "JSON" format. It will take some time before facebook processes the download request, then allows it.

2. After downloading facebook info, before running the script make sure the module "fpdf2" is installed. It can simply be installed with the command `pip install fpdf2`

3. Finally run the script. From the folder picker,first select "your_facebook_activity", then go to your "your_facebook_activity" -> messages -> the user folder.
4. Choose your name, must !!
5. Give nicknames if needed.

And it should be good to go.


## -------
This script only keeps text messages, shared photos, and timestamps. No representations of videos, reactions, files, links.
May work on them in the future.
Also, this script is meant to create pdfs readable with smartphones. So for computers, the font size may seem too much.
