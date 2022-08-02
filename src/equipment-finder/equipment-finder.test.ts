const Jimp = require("jimp");
const cv = require("opencv-ts");
const Finder = require("./equipment-finder");

describe('the equipment finder', () => {
  beforeAll(async () => {
    await new Promise((r) => {
      cv.onRuntimeInitialized = () => {
        r(undefined)
      }
    })
  })
  it('should find a ratnik helmet', async () => {
    const screen = await Jimp.read('./src/__test__/stash-screenshot-gear.png')
    const mat = cv.matFromImageData(screen.bitmap)
    const helmets = await Finder.getWornEquipment(mat)

    expect(helmets.some((h) => h.name === '6B47 Ratnik-BSh helmet')).toBeTruthy()
  })
})
