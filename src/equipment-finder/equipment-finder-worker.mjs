import cv from "opencv-ts";
import workerpool from 'workerpool'

function runTemplateMatch(src, template) {
  const dst = new cv.Mat()
  const mask = new cv.Mat()

  cv.matchTemplate(src, template, dst, cv.TM_CCOEFF, mask)
  const result = cv.minMaxLoc(dst, mask)

  dst.delete()
  mask.delete()
  template.delete()

  return result
}

workerpool.worker({
  runTemplateMatch
})
