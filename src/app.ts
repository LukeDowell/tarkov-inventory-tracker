import screenshot from 'screenshot-desktop'
import Jimp from 'jimp'
import * as fs from "fs";

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
