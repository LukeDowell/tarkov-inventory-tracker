const workerpool = require('workerpool');
const cv = require('opencv-ts')

function runTemplateMatch(srcData, templateData) {
  if (workerpool.isMainThread) console.error("reee main thread")
  const src = cv.matFromImageData(srcData)
  const template = cv.matFromImageData(templateData)
  const dst = new cv.Mat()
  const mask = new cv.Mat()

  cv.matchTemplate(src, template, dst, cv.TM_CCOEFF, mask)
  const result = cv.minMaxLoc(dst, mask)

  src.delete()
  template.delete()
  dst.delete()
  mask.delete()

  return result
}

workerpool.worker({
  runTemplateMatch
})
