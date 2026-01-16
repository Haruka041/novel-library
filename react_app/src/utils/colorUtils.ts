// 颜色工具函数

// 将HEX颜色转换为HSL
export function hexToHsl(hex: string): { h: number; s: number; l: number } {
  // 移除 # 符号
  hex = hex.replace(/^#/, '')
  
  // 解析 RGB
  const r = parseInt(hex.slice(0, 2), 16) / 255
  const g = parseInt(hex.slice(2, 4), 16) / 255
  const b = parseInt(hex.slice(4, 6), 16) / 255
  
  const max = Math.max(r, g, b)
  const min = Math.min(r, g, b)
  let h = 0
  let s = 0
  const l = (max + min) / 2
  
  if (max !== min) {
    const d = max - min
    s = l > 0.5 ? d / (2 - max - min) : d / (max + min)
    
    switch (max) {
      case r:
        h = ((g - b) / d + (g < b ? 6 : 0)) / 6
        break
      case g:
        h = ((b - r) / d + 2) / 6
        break
      case b:
        h = ((r - g) / d + 4) / 6
        break
    }
  }
  
  return { h: h * 360, s: s * 100, l: l * 100 }
}

// 将HSL转换为HEX
export function hslToHex(h: number, s: number, l: number): string {
  h = h / 360
  s = s / 100
  l = l / 100
  
  let r, g, b
  
  if (s === 0) {
    r = g = b = l
  } else {
    const hue2rgb = (p: number, q: number, t: number) => {
      if (t < 0) t += 1
      if (t > 1) t -= 1
      if (t < 1/6) return p + (q - p) * 6 * t
      if (t < 1/2) return q
      if (t < 2/3) return p + (q - p) * (2/3 - t) * 6
      return p
    }
    
    const q = l < 0.5 ? l * (1 + s) : l + s - l * s
    const p = 2 * l - q
    r = hue2rgb(p, q, h + 1/3)
    g = hue2rgb(p, q, h)
    b = hue2rgb(p, q, h - 1/3)
  }
  
  const toHex = (x: number) => {
    const hex = Math.round(x * 255).toString(16)
    return hex.length === 1 ? '0' + hex : hex
  }
  
  return `#${toHex(r)}${toHex(g)}${toHex(b)}`
}

// 生成莫兰迪风格的颜色（降低饱和度，调整亮度）
export function toMorandiColor(baseColor: string, variant: number = 0): string {
  const hsl = hexToHsl(baseColor)
  
  // 莫兰迪风格：降低饱和度到30-45%，亮度调整到50-65%
  const targetSaturation = 35 + (variant % 3) * 5 // 35%, 40%, 45%
  const targetLightness = 55 + (variant % 4) * 4 // 55%, 59%, 63%, 67%
  
  // 保持色相不变，调整饱和度和亮度
  return hslToHex(hsl.h, targetSaturation, targetLightness)
}

// 根据主题色生成一组莫兰迪色调（用于无封面书籍）
export function generateMorandiPalette(primaryColor: string): string[] {
  const hsl = hexToHsl(primaryColor)
  const palette: string[] = []
  
  // 生成6种变体，保持色相相近但有微妙变化
  for (let i = 0; i < 6; i++) {
    const hueShift = (i - 3) * 5 // -15, -10, -5, 0, 5, 10
    const newHue = (hsl.h + hueShift + 360) % 360
    const saturation = 30 + (i % 3) * 8 // 30%, 38%, 46%
    const lightness = 52 + (i % 4) * 5 // 52%, 57%, 62%, 67%
    
    palette.push(hslToHex(newHue, saturation, lightness))
  }
  
  return palette
}

// 从图片提取主色调（使用Canvas）
export async function extractDominantColor(imageUrl: string): Promise<string> {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.crossOrigin = 'Anonymous'
    
    img.onload = () => {
      const canvas = document.createElement('canvas')
      const ctx = canvas.getContext('2d')
      if (!ctx) {
        reject(new Error('无法创建Canvas上下文'))
        return
      }
      
      // 缩小图片以提高性能
      const maxSize = 50
      const scale = Math.min(maxSize / img.width, maxSize / img.height)
      canvas.width = Math.floor(img.width * scale)
      canvas.height = Math.floor(img.height * scale)
      
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height)
      
      const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height)
      const data = imageData.data
      
      // 简单的颜色统计
      let r = 0, g = 0, b = 0, count = 0
      
      for (let i = 0; i < data.length; i += 4) {
        // 跳过接近白色或黑色的像素
        const pixelR = data[i]
        const pixelG = data[i + 1]
        const pixelB = data[i + 2]
        
        const brightness = (pixelR + pixelG + pixelB) / 3
        if (brightness > 30 && brightness < 225) {
          r += pixelR
          g += pixelG
          b += pixelB
          count++
        }
      }
      
      if (count === 0) {
        resolve('#1976d2') // 默认蓝色
        return
      }
      
      r = Math.round(r / count)
      g = Math.round(g / count)
      b = Math.round(b / count)
      
      const hex = `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`
      resolve(hex)
    }
    
    img.onerror = () => {
      reject(new Error('图片加载失败'))
    }
    
    img.src = imageUrl
  })
}
