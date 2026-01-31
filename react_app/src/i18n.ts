import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import zhCN from './locales/zh-CN.json'
import zhTW from './locales/zh-TW.json'
import en from './locales/en.json'
import ja from './locales/ja.json'
import ru from './locales/ru.json'
import ko from './locales/ko.json'

const resources = {
  'zh-CN': { translation: zhCN },
  'zh-TW': { translation: zhTW },
  en: { translation: en },
  ja: { translation: ja },
  ru: { translation: ru },
  ko: { translation: ko },
}

const normalizeLanguage = (input?: string) => {
  if (!input) return 'zh-CN'
  const value = input.toLowerCase()
  if (value.startsWith('zh')) {
    if (value.includes('tw') || value.includes('hk') || value.includes('mo') || value.includes('hant')) {
      return 'zh-TW'
    }
    return 'zh-CN'
  }
  if (value.startsWith('en')) return 'en'
  if (value.startsWith('ja') || value.startsWith('jp')) return 'ja'
  if (value.startsWith('ru')) return 'ru'
  if (value.startsWith('ko') || value.startsWith('kr')) return 'ko'
  return 'zh-CN'
}

const detectInitialLanguage = () => {
  if (typeof window === 'undefined') return 'zh-CN'
  const saved = window.localStorage.getItem('sooklib-language') || window.localStorage.getItem('i18nextLng')
  return normalizeLanguage(saved || navigator.language)
}

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: detectInitialLanguage(),
    fallbackLng: 'zh-CN',
    interpolation: { escapeValue: false },
  })

i18n.on('languageChanged', (lng) => {
  if (typeof document !== 'undefined') {
    document.documentElement.lang = lng
  }
  if (typeof window !== 'undefined') {
    window.localStorage.setItem('sooklib-language', lng)
  }
})

export default i18n
