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
