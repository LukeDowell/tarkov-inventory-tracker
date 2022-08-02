import Jimp from "jimp"
import { getWornEquipment } from "./equipment-finder"

describe('the equipment finder', () => {
  it('should find a ratnik helmet', async () => {
    const screen = await Jimp.read('./src/__test__/stash-screenshot-gear.png')
    const helmets = await getWornEquipment(screen.bitmap as any)

    expect(helmets.some((h) => h.name === '6B47 Ratnik-BSh helmet')).toBeTruthy()
  })
})
