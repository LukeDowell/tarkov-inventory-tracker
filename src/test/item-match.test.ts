import cv from 'opencv-ts'
import Jimp from "jimp";

describe('a template matching example', () => {
  let srcImg
  let templImg
  let src
  let templ

  beforeAll(async () => {
    const start = new Date()
    console.log(`Start Time ${start.getTime()}`)

    srcImg = await Jimp.read('./src/test/stash-screenshot-gear.png')
    templImg = await Jimp.read('./data/template/6b47.png')

    let startProcessing = new Date();
    console.log(`Image Load Time Ms ${startProcessing.getTime() - start.getTime()}`)
    src = cv.matFromImageData(srcImg.bitmap as any)
    templ = cv.matFromImageData(templImg.bitmap as any)
  })

  afterAll(() => {
    src.delete()
    templ.delete()
  })

  it('should match a 6b47 helmet',  () => {
    const dst = new cv.Mat()
    const mask = new cv.Mat()

    const startProcessing = new Date()
    cv.matchTemplate(src, templ, dst, cv.TM_CCOEFF, mask)
    const result = cv.minMaxLoc(dst, mask)

    console.log(`Time To Result - Ms ${new Date().getTime() - startProcessing.getTime()}`)

    const maxPoint = result.maxLoc
    const point = new cv.Point(maxPoint.x + templ.cols, maxPoint.y + templ.rows)

    dst.delete()
    mask.delete()

    expect([point.x, point.y]).toEqual([846, 127])
  })
})
