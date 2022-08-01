import screenshot from 'screenshot-desktop'
import Jimp from 'jimp'
import cv from "opencv-ts";

const canvas = <HTMLCanvasElement> document.getElementById('canvas')
canvas.width = window.innerWidth
canvas.height = window.innerHeight
const ctx = canvas.getContext('2d')
ctx.strokeStyle = "#FF0000";

console.log("Reading in UI templates...")

const uiTemplates = [Jimp.read('./data/template/ui/headwear.png')]

cv.onRuntimeInitialized = () => { // https://stackoverflow.com/questions/56671436/cv-mat-is-not-a-constructor-opencv
  Promise.all(uiTemplates).then((jimps) => {
    let startTime = new Date().getTime();
    const headwearTemplate = cv.matFromImageData(jimps[0].bitmap as any)

    window.setInterval(() => {
        screenshot()
          .then((buf: Buffer) => Promise.resolve(Jimp.read(buf)))
          .then((image: Jimp) => {
            const screenshotMat = cv.matFromImageData(image.bitmap as any)
            const dst = new cv.Mat()
            const mask = new cv.Mat()

            cv.matchTemplate(screenshotMat, headwearTemplate, dst, cv.TM_CCOEFF, mask)

            const result = cv.minMaxLoc(dst, mask)
            const tw = headwearTemplate.cols
            const th = headwearTemplate.rows

            ctx.clearRect(0, 0, canvas.width, canvas.height)
            ctx.strokeRect(
              result.maxLoc.x,
              result.maxLoc.y,
              tw,
              th
            )

            console.log(`Found Headwear @ ${result.maxLoc.x},${result.maxLoc.y} in ${new Date().getTime() - startTime}`)
          })
          .catch((err)   => { throw err })
      },
      1500
    )
  })
}
