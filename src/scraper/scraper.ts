import cheerio from 'cheerio'
import {ArmorClass, ArmorMaterial, Helmet, HelmetArea, RicochetChance, SoundReduction} from "../gear";
import Element = cheerio.Element;
import Crawler from 'crawler'
import Root = cheerio.Root;
import * as fs from "fs";


/////////////
// CRAWLER //
/////////////

const crawler = new Crawler({ maxConnections: 10 })
const imageCrawler = new Crawler({ maxConnections: 5, encoding: null, jQuery: false })

crawler.queue([{
  uri: 'https://escapefromtarkov.fandom.com/wiki/Headwear',
  callback: (err, res, done) => {
    if (err) console.error(err)
    else {
      console.log(`Retrieved Helmet page at ${new Date().getTime()}`)
      const helmetData = scrapeHelmets(cheerio.load(res.body))
      helmetData.forEach((h, i) => {
        if (h.iconUrl.includes('data:image/gif')) {
          console.log(`Skipping ${h.name} due to gif icon`)
          return
        }

        console.log(`queueing image ${i} ${h.iconUrl}`)
        imageCrawler.queue([{ uri: h.iconUrl, callback: imageDownloadCallback(h.name) }])
      })
    }

    done()
  }
}])

const imageDownloadCallback = (name: string) => async (err, res, done) => {
  console.log(`Downloading image for ${name} at ${new Date().getTime()}`)

  if(err) {
    console.error(err.stack);
    done()
    return
  }

  try {
    const writeStream = fs.createWriteStream(`./data/template/${name}.png`);
    if (!writeStream.write(res.body)) {
      console.log(`WAITING on ${name}`)
      await new Promise((resolve) => {
        writeStream.on('drain', () => {
          console.log(`DONE WAITING on ${name}`)
          resolve(undefined)
        })
      })
    }
    console.log(`Finished saving image for ${name} at ${new Date().getTime()}`)
  } catch (err) {
    console.error(`ERROR saving image for ${name} at ${new Date().getTime()}`)
    console.error(err)
  } finally {
    done()
  }
}

/////////////
// HELMETS //
/////////////

export function scrapeHelmets($: Root): Array<Helmet & { iconUrl: string }> {
  return $('#Armored').parent().next().children('tbody').children()
    .toArray()
    .map(rowToHelmet)
    .filter((h): h is Helmet & { iconUrl: string } => !!h)
}

function rowToHelmet(rowElement: Element): Helmet & { iconUrl: string } | undefined {
  const $ = cheerio.load(rowElement)
  try {
    const maybeIconUrl = $('img').attr('src')
    const iconUrl = maybeIconUrl.includes('data:image/gif') ? $('img').attr('data-src') : maybeIconUrl
    return {
      name: sanitizeText($('a').attr('title')),
      material: sanitizeText($('td:nth-child(3)').text()) as ArmorMaterial,
      class: parseInt(sanitizeText($('td:nth-child(4)').text())) as ArmorClass,
      areas: sanitizeText($('td:nth-child(5)').text()).replace(' ', '').split(',') as HelmetArea[],
      durability: parseInt(sanitizeText($('td:nth-child(6)').text())),
      effectiveDurability: parseInt(sanitizeText($('td:nth-child(7)').text())),
      ricochetChance: sanitizeText($('td:nth-child(8)').text()) as RicochetChance,
      movementSpeedPenalty: parseInt(sanitizeText($('td:nth-child(9)').text())),
      turningSpeedPenalty: parseInt(sanitizeText($('td:nth-child(10)').text())),
      ergonomicsPenalty: parseInt(sanitizeText($('td:nth-child(11)').text())),
      soundReductionPenalty: sanitizeText($('td:nth-child(12)').text()) as SoundReduction,
      blocksHeadset: sanitizeText($('td:nth-child(13)').text()) === 'Yes',
      weight: parseFloat(sanitizeText($('td:nth-child(14)').attr('data-sort-value'))),
      iconUrl
    }
  } catch (err) {
    console.error(`Error while parsing helmet row: ${err}`)
    return undefined
  }
}

function sanitizeText(s: string): string {
  return s.replace(/%/, '')
    .replace('\r', '')
    .replace('\n', '')
    .replace(/['"]+/g, '')
    .trim()
}
