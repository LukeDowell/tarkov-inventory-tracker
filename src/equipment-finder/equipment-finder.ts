import Jimp from "jimp"
import cv from 'opencv-ts'
import fs from 'fs'
import workerpool from 'workerpool'
import {Helmet} from "../gear";

const equipmentContext = {
  "helmet": {
    uiTemplate: new Promise((r) => Jimp.read('./data/template/ui/headwear.png').then((i) => r(cv.matFromImageData(i.bitmap as any)))),
    equipmentTemplates: buildEquipmentTemplates("helmet")
  }
}

async function buildEquipmentTemplates(equipment): Promise<Map<string, ImageData>> {
  const startDate = new Date().getTime()
  console.log(`Start time for ${equipment} is ${startDate}`)
  return new Promise((r) => {
    fs.readdir(`./data/template/${equipment}`, (err, files) => {
      if (err) throw err
      const futureFileImages = files.map((fileName) => Jimp.read(`./data/template/${equipment}/${fileName}`)
        .then((i) => [fileName, i]))
        .map((p) => p.then((fileImage) => {
          const jimg = fileImage[1] as Jimp
          return [fileImage[0] as string, jimg.bitmap]
        }))

      Promise.all(futureFileImages).then((fileImages) => {
        let map: Map<string, ImageData> = new Map<string, ImageData>()
        fileImages.forEach((fileImage) => {
          map[fileImage[0] as string] = fileImage[1]
        })

        console.log(`Finished ingesting ${equipment} in ${new Date().getTime() - startDate}`)
        r(map)
      })
    })
  })
}

const pool = workerpool.pool(
  `${__dirname}/equipment-finder-worker.js`,
  {
    minWorkers: 8,
    workerType: "thread"
  }
)

export async function getWornEquipment(src: ImageData): Promise<Helmet[]> {
  return new Promise((resolve) => {
    equipmentContext.helmet.equipmentTemplates.then((helmetTemplates) => {
      const futureResults = []

      for (const prop in helmetTemplates as any) {
        const startTime = new Date().getTime()
        const futureResult = pool.proxy()
          .then((w) => {
            console.log(`Running ${prop} at ${new Date().getTime() - startTime}`)
            w.runTemplateMatch(cv.matFromImageData(src), helmetTemplates[prop])
          })
          .then((r) => {
            console.log(`${prop} took ${new Date().getTime() - startTime} ms`)
            return [prop, r]
          })
          .catch((e) => console.error(e))
        futureResults.push(futureResult)
      }

      Promise.all(futureResults).then((results) => {
        resolve(results)
      })
    })
  })
}
