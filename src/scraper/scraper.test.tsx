import {scrapeHelmets} from "./scraper";
import * as fs from "fs";

describe('the scraper', () => {
  it('should parse the headwear page', async () => {
    const page: Buffer = await new Promise((r) => fs.readFile('./src/scraper/Headwear.html', (e, d) => r(d)))
    const result = scrapeHelmets(page)

    const expected = {
      name: "Tac-Kek FAST MT helmet (replica)",
      material: "Combined materials",
      class: 1,
      areas: ["Top", "Nape"],
      durability: 40,
      effectiveDurability: 80,
      ricochetChance: "High",
      movementSpeedPenalty: 0,
      turningSpeedPenalty: 0,
      ergonomicsPenalty: -1,
      soundReductionPenalty: "None",
      blocksHeadset: false,
      weight: 0.45,
      iconUrl: './Headwear/TK_FAST_Icon.png'
    };

    expect(result).toContainEqual(expected)
  })
})
