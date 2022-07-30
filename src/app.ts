import screenshot from 'screenshot-desktop'
import cv from 'opencv-ts'
import Jimp from 'jimp'

let startTime = new Date().getTime();
screenshot()
  .then((buf: Buffer) => {
    console.log(`Screenshot ${new Date().getTime() - startTime} milliseconds`)
    return Promise.resolve(Jimp.read(buf))
  })
  .then((image: Jimp) => {
    console.log(`Total ${new Date().getTime() - startTime} milliseconds`)
  })
  .catch((err)   => { throw err })
