import cv from 'opencv-ts'
import Jimp from "jimp";

describe('a template matching example', () => {
  it('should match a 6b47 helmet',  async () => {
    const srcImg = await Jimp.read('./src/__test__/stash-screenshot-gear.png')
    const src = cv.matFromImageData(srcImg.bitmap as any)
    const templImg = await Jimp.read('./src/__test__/6b47-test.png')
    const templ = cv.matFromImageData(templImg.bitmap as any)

    const dst = new cv.Mat()
    const mask = new cv.Mat()
    cv.matchTemplate(src, templ, dst, cv.TM_CCOEFF, mask)
    const result = cv.minMaxLoc(dst, mask)

    const maxPoint = result.maxLoc

    dst.delete()
    mask.delete()
    templ.delete()
    src.delete()

    expect(result).toBeTruthy()
    expect([maxPoint.x, maxPoint.y]).toEqual([922, 189])
  })

  it('should not match a 6b3tm-01m armored rig',  async () => {
    const srcImg = await Jimp.read('./src/__test__/stash-screenshot-gear.png')
    const src = cv.matFromImageData(srcImg.bitmap as any)
    const templImg = await Jimp.read('./src/__test__/6b3tm-01m-test.png')
    const templ = cv.matFromImageData(templImg.bitmap as any)

    const dst = new cv.Mat()
    const mask = new cv.Mat()
    cv.matchTemplate(src, templ, dst, cv.TM_CCOEFF, mask)
    const result = cv.minMaxLoc(dst, mask)

    const maxPoint = result.maxLoc
    const point = new cv.Point(maxPoint.x + templ.cols, maxPoint.y + templ.rows)

    dst.delete()
    mask.delete()
    templ.delete()
    src.delete()

    expect(result).toBeTruthy()
    expect([point.x, point.y]).toEqual([0, 0])
  })
})
