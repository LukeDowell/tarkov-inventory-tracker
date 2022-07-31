import cheerio from 'cheerio'
import {ArmorClass, ArmorMaterial, Helmet, HelmetArea, RicochetChance, SoundReduction} from "../gear";
import Element = cheerio.Element;

/////////////
// HELMETS //
/////////////

export function scrapeHelmets(page: string | Buffer): Array<Helmet & { iconUrl: string }> {
  return cheerio.load(page)('#Armored').parent().next('.table-wide').find('tbody').children()
    .toArray()
    .map(rowToHelmet)
    .filter((h): h is Helmet & { iconUrl: string } => !!h)
}

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
