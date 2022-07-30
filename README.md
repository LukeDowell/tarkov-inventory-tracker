## Tarkov Image Processor

Pretty awful name, nice. The general idea of this app is to use OpenCV's template matching to parse screenshots of 
Tarkov in order to keep track of player statistics. I'd like to be able to tell users things like:
 * Your favorite loadout is X
 * Your most common armor class is X, when you use X+1, you survive Y% more often
 * Survival rate for using weapon X is Y%

I don't even have a proof of concept yet, some concerns I have:

 * How fast is the evaluation? Does it negatively impact Tarkov?
 * How does different resolutions affect the image parsing?
 * How do I efficiently take screenshots of a running application? Is BattleEye or BSG going to hate that? Will I need
    to use native Windows modules?
 
I think the first order of business is going to be to take some screenshots in-game and get a PoC running. 

1. Set up a test of opencv that can find some random item in tarkov consistently from a screenshot.
2. Find a way to automatically grab screenshots from a running application
3. Implement an interface similar to getCurrentEquipment() -> json blob of items player is wearing
4. Find a way to track player "state", are they in raid, is the stash open, are we on the medical screen, etc
5. Write a crawler to download image files and metadata for every tarkov item. I wonder if this could be extracted from
   the game cache...
6. ???



## 07/29/2022

First issue! I'm trying to dev on WSL 2, but the app is going to run exclusively on Windows. I get a weird error when
trying to use the screenshot library I'm consuming:

```
 npm run start

> tarkov-image-processor@1.0.0 start
> tsc && node dist/app.js

node:internal/errors:841
  const err = new Error(message);
              ^

Error: Command failed: xrandr
/bin/sh: 1: xrandr: not found
```

I copied the code over to windows and it worked just fine, so I think for this app in particular I'm going to do the 
dev on Windows. The good news is that it did in fact work on Windows and grabbed a screenshot of the tarkov screen.
Windows defender did not like it though; I'm guessing there are going to be ways to digitally "sign" the released .exe
to hopefully get rid of any antivirus warnings in the future.

I'm excited to start writing some tests for these image comparisons. I'm going to start by just comparing the exact 
"inventory image" of the item. I'm hoping that goes well and is super fast and accurate, but if it is not, I think there
are a lot of things we will be able to try. It may end up being helpful to extract the "black and white" text from all images
and just use that.


## 07/29/2022 wow i was up late last night

I have tinkered around with the screenshot library a bit and it seems to be pretty dang quick, the retrieval of the 
screenshot on my 3440x1440 screen takes about 2-5 milliseconds which is wayyyy better than I was even hoping for.

My next problem is piping that data to opencv. First off, I'm using opencv-js which feels pretty second-class to the .net
community. I am getting this screenshot data as a `Buffer` and I need to get opencv to parse that somehow. I'm a little
nervous about getting errors that are hard to diagnose, especially considering I feel pretty weak in this area. I
could probably blow past this issue by writing the screenshot to disk and having opencv parse that, but I will lose my mind
because of how inefficient that is. 

Exciting news, found one of the tutorial pages on OpenCV that shows how to load in an image using `Jimp`, another image
library. Jimp seems to be able to import the buffer from the screenshot library just fine, so I think we are off to the 
races. An odd bit about Jimp is that their own documentation recommends you import it as a default type, and that type
is also the type that is returned from the 'static' methods used to ingest images:

```typescript
import Jimp from 'jimp'

screenshot()
  .then((buf: Buffer) => Promise.resolve(Jimp.read(buf)))
  .then((image: Jimp) => console.log(image.getMIME()))
  .catch((err) => { throw err })
```

Seems to work though, so it's all good with me! Unfortunately this step has raised the processing time by two orders of 
magnitude and we are now sitting at ~500ms just to execute the two lines above. That's already digging pretty deep into
my performance goal of being able to run this processor twice a second. 

I dug into the screenshot code a bit and I must have totally misread the timestamp before, I added some nicer formatting
and discovered that the screenshot itself takes about ~150 milliseconds on a monitor with my resolution. I looked at 
how the library itself was working and basically there is a .bat file embedded in the library that is responsible for 
actually retrieving the bitmap of the image. I'd like to be able to tinker with things like not converting the bitmap at
all, taking partial screenshots, using different win32 api calls, etc, so I am probably just going to rob the library of
this .bat file and consume it on my own. I'm a little nervous about how long OpenCV is going to take, I am worried about
anything longer than 1 second on my machine since it's fairly powerful and I doubt the average user is going to get faster
processing times than myself.

Okay I took a break, came back and reread this, and realized that I am being an insane person. Why am I caring about 500ms
vs 1 second vs 2 second when I don't even have the core of the app. 

## 07/30/2022

I got a test up and running, using a template image it is able to find the helmet successfully! I really should look up
a bit about how it actually works, the coordinates returned from the result are the exact same every time. I am not sure
why but I was expecting there to be a bit of variation between runs. Loading up the image in Jimp and having OpenCV ingest
the bitmap takes about 8 seconds, and the comparison takes about 800ms. 

Something is gonna have to be done about performance, I know I was saying it was premature yesterday but there is just no
way I'm gonna have something useful if each item takes 1 second. I need to be able to search 100s of items quickly. I'm
hoping that image size drastically impacts the timing, if it does then I am probably just going to move ahead with my 
idea of using just the black-and-white text to find images. Then I can modify the screenshot utility to only take a picture
of the left half of the screen, and hopefully we will have a usable processing time.
