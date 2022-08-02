const Jimp = require("jimp")
const fs = require('fs')
const cv = require('../lib/opencv')
const workerpool = require('workerpool')

const equipmentContext = {
  "helmet": {
    uiTemplate: new Promise((r) => Jimp.read('./data/template/ui/headwear.png').then((i) => r(cv.matFromImageData(i.bitmap)))),
    equipmentTemplates: buildEquipmentTemplates("helmet")
  }
}

async function buildEquipmentTemplates(equipment) {
  return new Promise((r) => {
    fs.readdir(`./data/template/${equipment}`, (err, files) => {
      if (err) throw err
      const futureFileImages = files.map((fileName) => Jimp.read(`./data/template/${equipment}/${fileName}`)
        .then((i) => [fileName, i]))
        .map((p) => p.then((fileImage) => {
          const jimg = fileImage[1]
          return [fileImage[0], cv.matFromImageData(jimg.bitmap)]
        }))

      Promise.all(futureFileImages).then((fileImages) => {
        let map = {}
        fileImages.forEach((fileImage) => {
          map[fileImage[0]] = fileImage[1]
        })

        r(map)
      })
    })
  })
}

const workers = []
const pool = workerpool.pool(`${__dirname}/equipment-finder-worker.mjs`)

async function getWornEquipment(src) {
  return new Promise((resolve) => {
    equipmentContext.helmet.equipmentTemplates.then((helmetTemplates) => {
      const futureResults = []

      for (const prop in helmetTemplates) {
        const futureResult = pool.exec('runTemplateMatch', [src, helmetTemplates[prop]])
          .then((r) => [prop, r])
          .catch((e) => console.error(e))
        futureResults.push(futureResult)
      }

      Promise.all(futureResults).then((results) => {
        resolve(results)
      })
    })
  })
}


module.exports = {
  getWornEquipment: getWornEquipment
}
