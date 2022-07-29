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
