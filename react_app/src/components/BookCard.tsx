import { Box, Card, CardContent, Typography, Skeleton, Chip } from '@mui/material'
import MenuBookIcon from '@mui/icons-material/MenuBook'
import { useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { BookSummary } from '../types'

interface BookCardProps {
  book?: BookSummary
  loading?: boolean
  onClick?: () => void
}

// Material Design 纯色方案
const COVER_COLORS = [
  '#5C6BC0', // 靛蓝
  '#AB47BC', // 紫色  
  '#EC407A', // 粉色
  '#EF5350', // 红色
  '#FF7043', // 深橙
  '#FFA726', // 橙色
  '#FFCA28', // 琥珀色
  '#66BB6A', // 绿色
  '#26A69A', // 青色
  '#42A5F5', // 蓝色
]

// 根据标题选择颜色
const getCoverColor = (title: string): string => {
  let hash = 0
  const titleStr = String(title || '')
  for (let i = 0; i < titleStr.length; i++) {
    hash = ((hash << 5) - hash) + titleStr.charCodeAt(i)
    hash = hash & hash
  }
  return COVER_COLORS[Math.abs(hash) % COVER_COLORS.length]
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
          // 纯色背景 + 图标 + 书名
          <Box
            sx={{
              width: '100%',
              height: '100%',
              bgcolor: getCoverColor(book.title),
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              p: 2,
            }}
          >
            {/* 书籍图标 */}
            <MenuBookIcon
              sx={{
                fontSize: { xs: 64, sm: 80 },
                color: 'rgba(255, 255, 255, 0.9)',
                mb: 2,
              }}
            />
            {/* 书名 */}
            <Typography
              sx={{
                fontSize: { xs: '0.85rem', sm: '0.95rem' },
                fontWeight: 500,
                color: 'rgba(255, 255, 255, 0.95)',
                textAlign: 'center',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                display: '-webkit-box',
                WebkitLineClamp: 3,
                WebkitBoxOrient: 'vertical',
                lineHeight: 1.4,
                px: 1,
                width: '100%',
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
