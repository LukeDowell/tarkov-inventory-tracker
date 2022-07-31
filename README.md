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

Uh oh, turns out I didn't have it working after all. Here is a snippet of the test:

```typescript
    const point = new cv.Point(maxPoint.x + templ.cols, maxPoint.y + templ.rows)

    dst.delete()
    mask.delete()
    templ.delete()

    expect([point.x, point.y]).toEqual([846, 127])
```

In this test case, turns out the `templ` image's size is 846x127. Upon inspecting the actual result of the template match
call, I discovered it's undefined. RIP. 

Okay that ended up being some async issues w/ Jest, I tried to load the image in a `beforeAll` but it caused the image
to not be there when the test was running. I plopped it all back in the test enclosure and now am starting to inspect 
my results. 

For the test where I SHOULD NOT find the template image, my result looks like this:

```
{
  "minVal": -50478908,
  "maxVal": 68386448,
  "minLoc": {
    "x": 2941,
    "y": 245
  },
  "maxLoc": {
    "x": 1991,
    "y": 65
  }
}
```

For the test where I SHOULD find the template image, my result looks like this:

```
{
  "minVal": -22742510,
  "maxVal": 37480360,
  "minLoc": {
    "x": 2671,
    "y": 402
  },
  "maxLoc": {
    "x": 719,
    "y": 0
  }
}
```


I popped open the stash image in GIMP and looked at some of the coordinates being output above. None of the coordinates
point where I would expect; the positive test case is sort of nearby the helmet but it is too
high. I'm wondering if there is some kind of offset in terms of me needing to account for image
size or something.  

While I was in Gimp I pulled out the text of the helmet and saved it. Using that instead of the full image nets me 
this result:

```
{
  "minVal": -2963167.5,
  "maxVal": 8348142,
  "minLoc": {
    "x": 880,
    "y": 733
  },
  "maxLoc": {
    "x": 922,
    "y": 189
  }
}
```

The maxLoc coordinates are right on the money! Cool stuff. I am wondering what the minVal and maxVal values 
are from; I saw a comment on a stackoverflow post that said they are measures of confidence, but the numbers
are very large and distance from one another. 

[The post in question](https://stackoverflow.com/questions/8520882/how-to-know-if-matchtemplate-found-an-object-or-not)

The answer:

    matchTemplate() returns a matrix whose values indicate the probability that your object is centered in that pixel.
    If you know the object (and only one object) is there, all you have to do is look for the location of the maximum value.
    
    If you don't know, you have to find the max value, and if it is above a certain threshold, your object should be there.
    
    Now, selection of that threshold is tricky - it's up to you to find the good threshold specifically for your app. 
    And of course you'll have some false positives (when there is no object, but the max is bigger than threshold), 
    and some false negatives (your object does not create a big enough peak)
    
    The way to choose the threshold is to collect a fairly large database of images with and without your object inside, 
    and make a statistic of how big is the peak when object is inside, and how big is when it isn't, and choose the
    threshold that best separates the two classes

I'm thinking of starting on the scraper that is going to pull down thumbnails for all these template images just to mix
up the work a bit. I remember having a teacher who was a fan of photoshop, and one day he showed us the "batch" processing
functionality that allowed him to modify different assets all at once. I'm wondering if I will be able to extract
the black-and-white item text in that fashion.

Before I forget, for completeness here is the result of the text for an item that is NOT on the screen:

```
{
  "minVal": -2654454.75,
  "maxVal": 3559548.5,
  "minLoc": {
    "x": 1353,
    "y": 605
  },
  "maxLoc": {
    "x": 1145,
    "y": 835
  }
}
```

The first thing I notice is that the relationship between the minVal and maxVal numbers aren't what I was expecting. If a 
larger maxVal indicates higher confidence, I would expect the negative test case with the full template image earlier to
have a lower value than it's opposite, positive test case. The test results before were not very good, although I am still a 
little weirded out.

Okay made some progress on the web crawler / scraper front, revel in it's glory:

```typescript
function rowToHelmet(rowElement: Element): Helmet & { iconUrl: string } | undefined {
  const $ = cheerio.load(rowElement)
  try {
    return {
      name: $('a').attr('title'),
      material: $('td:nth-child(3)').text().replace('\n', '') as ArmorMaterial,
      class: parseInt($('td:nth-child(4)').text().replace('\n', '')) as ArmorClass,
      areas: $('td:nth-child(5)').text().replace('\n', '').replace(' ', '').split(',') as HelmetArea[],
      durability: parseInt($('td:nth-child(6)').text().replace('\n', '')),
      effectiveDurability: parseInt($('td:nth-child(7)').text().replace('\n', '')),
      ricochetChance: $('td:nth-child(8)').text().replace('\n', '') as RicochetChance,
      movementSpeedPenalty: parseInt($('td:nth-child(9)').text().replace('\n', '').replace('%', '')),
      turningSpeedPenalty: parseInt($('td:nth-child(10)').text().replace('\n', '').replace('%', '')),
      ergonomicsPenalty: parseInt($('td:nth-child(11)').text().replace('\n', '').replace('%', '')),
      soundReductionPenalty: $('td:nth-child(12)').text().replace('\n', '') as SoundReduction,
      blocksHeadset: $('td:nth-child(13)').text().replace('\n', '') === 'Yes',
      weight: parseFloat($('td:nth-child(14)').attr('data-sort-value')),
      iconUrl: $('img').attr('src'),
    }
  } catch (err) {
    console.error(`Error while parsing helmet row: ${err}`)
    return undefined
  }
}
```

Cheerio worked perfectly, very neat. Now to test the crawler aspect, I'm curious to see how it works in terms of concurrent
image downloads. Things I need to think about moving forward:

1. Check out SQLite, if we are going to be keeping track of user data over a long period of time, that might be a nice
   way to go about it
2. Investigate how image size affects the ability to template-match. I'm wondering if my bad results from the first 
   matching tests had anything to do with the actual sizes of the images not matching up. I'm not even sure if that would matter,
   I may have to do some resizing w/ Jimp or figure out a standard ratio going forward.
3. Bulk processing of these images in order to extract the black and white text. It would be neat if I could commit 
   whatever that solution ends up being...

## 07/31/2022

Interesting, I am seeing different results using the crawler than I am with my browser. Part of my code selects the nearest
image inside of a table row, finds its source, and assumes that is the icon image for the given piece of gear. In my browser
most of these URLs are pretty normal: [Altyn Image](https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/2/2d/AltynHelmetIcon.png/revision/latest?cb=20180517203714)

I took the response of the crawler and replaced my test file's contents with the response's body and noticed the URLs are 
different: `data:image/gif;base64,R0lGODlhAQABAIABAAAAAP///yH5BAEAAAEALAAAAAABAAEAQAICTAEAOw%3D%3D`

I wonder what is up with that? What is also weird is that the very first entry in the table has an image, but none of the
others do. My first thought is that this is actually anti-crawler behavior to help protect their bandwidth, which would
maybe be a little annoying but not that bad. I can just use a headless browser to gather the image URLs and then still
just pass them to Crawler if I wish. 
