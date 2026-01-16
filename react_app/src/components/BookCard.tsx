import { Box, Card, CardContent, Typography, Skeleton, Chip } from '@mui/material'
import { useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { BookSummary } from '../types'
import { useSettingsStore } from '../stores/settingsStore'

interface BookCardProps {
  book?: BookSummary
  loading?: boolean
  onClick?: () => void
}

// 生成颜色的哈希函数
const stringToColor = (str: string): string => {
  let hash = 0
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash)
  }
  const hue = hash % 360
  return `hsl(${hue}, 45%, 50%)`
}

// 生成渐变封面
const generateGradientCover = (title: string) => {
  const color1 = stringToColor(title)
  const color2 = stringToColor(title + 'salt')
  return `linear-gradient(135deg, ${color1} 0%, ${color2} 100%)`
}

export default function BookCard({ book, loading = false, onClick }: BookCardProps) {
  const navigate = useNavigate()
  const [imageError, setImageError] = useState(false)

  if (loading) {
    return (
      <Card sx={{ height: '100%' }}>
        <Skeleton variant="rectangular" sx={{ aspectRatio: '2/3' }} />
        <CardContent sx={{ p: 1.5 }}>
          <Skeleton width="80%" />
          <Skeleton width="60%" />
        </CardContent>
      </Card>
    )
  }

  if (!book) return null

  const handleClick = () => {
    if (onClick) {
      onClick()
    } else {
      navigate(`/book/${book.id}`)
    }
  }

  const showFallback = !book.cover_url || imageError

  // 获取书名首字作为封面文字
  const getFirstChar = (title: string): string => {
    if (!title) return '?'
    // 优先取中文字符，否则取第一个字符
    const match = title.match(/[\u4e00-\u9fa5]/)
    return match ? match[0] : title[0].toUpperCase()
  }

  return (
    <Card
      sx={{
        height: '100%',
        cursor: 'pointer',
        transition: 'transform 0.2s, box-shadow 0.2s',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: 4,
        },
      }}
      onClick={handleClick}
    >
      {/* 封面图 */}
      <Box
        sx={{
          aspectRatio: '2/3',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        {showFallback ? (
          // 渐变封面 + 文字
          <Box
            sx={{
              width: '100%',
              height: '100%',
              background: generateGradientCover(book.title),
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              padding: 2,
            }}
          >
            {/* 大字符 */}
            <Typography
              sx={{
                fontSize: '4rem',
                fontWeight: 'bold',
                color: 'white',
                textShadow: '2px 2px 4px rgba(0,0,0,0.3)',
                mb: 1,
              }}
            >
              {getFirstChar(book.title)}
            </Typography>
            {/* 书名 */}
            <Typography
              variant="caption"
              sx={{
                color: 'white',
                textAlign: 'center',
                textShadow: '1px 1px 2px rgba(0,0,0,0.5)',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                display: '-webkit-box',
                WebkitLineClamp: 3,
                WebkitBoxOrient: 'vertical',
                lineHeight: 1.2,
                fontWeight: 500,
              }}
            >
              {book.title}
            </Typography>
          </Box>
        ) : (
          <Box
            component="img"
            src={`/api${book.cover_url}`}
            alt={book.title}
            sx={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
            }}
            onError={() => setImageError(true)}
          />
        )}

        {/* 新书标签 */}
        {book.is_new && (
          <Chip
            label="NEW"
            size="small"
            color="secondary"
            sx={{
              position: 'absolute',
              top: 8,
              right: 8,
              fontSize: '0.65rem',
              height: 20,
            }}
          />
        )}

        {/* 格式标签 */}
        {book.file_format && (
          <Chip
            label={book.file_format.toUpperCase()}
            size="small"
            sx={{
              position: 'absolute',
              bottom: 8,
              left: 8,
              fontSize: '0.65rem',
              height: 20,
              bgcolor: 'rgba(0,0,0,0.7)',
              color: 'white',
            }}
          />
        )}
      </Box>

      {/* 书籍信息 */}
      <CardContent sx={{ p: 1.5 }}>
        <Typography
          variant="body2"
          fontWeight="medium"
          sx={{
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
            lineHeight: 1.3,
            minHeight: '2.6em',
          }}
        >
          {book.title}
        </Typography>
        {book.author_name && (
          <Typography
            variant="caption"
            color="text.secondary"
            sx={{
              display: 'block',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
              mt: 0.5,
            }}
          >
            {book.author_name}
          </Typography>
        )}
      </CardContent>
    </Card>
  )
}
