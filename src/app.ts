import screenshot from 'screenshot-desktop'
import fs from 'fs'

screenshot().then((img) => {
  console.log(`Start - ${new Date()}`)
  fs.writeFile('out.jpg', img,  (err) => {
    console.log(`Image Retrieved - ${new Date()}`)
    if (err) {
      throw err
    }
    console.log('written to out.jpg')
  })
}).catch((err) => {
  throw err
})
