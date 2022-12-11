# Project
Hello everyone This is a huge script creator of groups for the VK social network. One person ordered it from me, but they didn't pay me, so now it will show off on the github. If someone needs more data on this project, you can email me:
**g6h6m238929@gmail.com**

## How to use this ~~shit~~ program?
It was assumed that these groups would be created from the left pages, because here you need to enter a large number of accounts. There is also proxy and 2Captcha support. The script works multithreaded using the asynchronous library *asyncio*

## How to fill in data files?
Initially, you need to fill in the *plugins\parameters\parameters file.json* and insert the file names and paths to the photos that will be used as the cover \avatar of the group (we will consider later). Files must be filled in this way:
Proxy:
```
ip:port:login:password

```

Group names:
```
Group names 1
Group names 2
Group names 3
Group names 4
Group names 5

```
Account logins and passwords:
```
login:password

```
<blockquote>At least that's how some stores with accounts sell. For example https://darkstore.su/ </blockquote>

## Let's look at the pictures
There are 3 types of photos here:
- Covers
- Avatars
- Photos for the album
All photos except the last one (*album photo*) will be resized so that your mountains (*for example*) on the avatar do not become the land that is also in the photo. All photos must be moved to folders (*default*) in
1. *special_raw/cover/* - for covers
2. *special_raw/avatar/* - for avatars
3. *images_raw/* - for regular photos in albums

<blackquote> This is a shitcode) </blackquote>