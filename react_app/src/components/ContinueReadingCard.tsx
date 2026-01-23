import { Box, Card, CardContent, Typography, LinearProgress, Skeleton } from '@mui/material'
import { useNavigate } from 'react-router-dom'
import { useMemo, useState } from 'react'
import { ContinueReadingItem } from '../types'
import { usePrimaryColor } from '../stores/themeStore'
import { generateMorandiPalette } from '../utils/colorUtils'

interface ContinueReadingCardProps {
  item?: ContinueReadingItem
  loading?: boolean
}

export default function ContinueReadingCard({ item, loading = false }: ContinueReadingCardProps) {
  const navigate = useNavigate()
  const [imageError, setImageError] = useState(false)
  const primaryColor = usePrimaryColor()
  const morandiPalette = useMemo(() => generateMorandiPalette(primaryColor), [primaryColor])

  if (loading) {
    return (
      <Card sx={{ display: 'flex', height: 120 }}>
        <Skeleton variant="rectangular" width={80} height={120} />
        <CardContent sx={{ flex: 1, p: 1.5 }}>
          <Skeleton width="70%" />
          <Skeleton width="50%" />
          <Skeleton width="30%" sx={{ mt: 2 }} />
        </CardContent>
      </Card>
    )
  }

  if (!item) return null

  const progressPercent = Math.round(item.progress * 100)
  const showFallback = !item.cover_url || imageError

  const getColorIndex = (title: string): number => {
    let hash = 0
    const titleStr = String(title || '')
    for (let i = 0; i < titleStr.length; i++) {
      hash = ((hash << 5) - hash) + titleStr.charCodeAt(i)
      hash = hash & hash
    }
    return Math.abs(hash) % 6
  }

  const coverColor = morandiPalette[getColorIndex(item.title)]

  return (
    <Card
      sx={{
        display: 'flex',
        height: 120,
        cursor: 'pointer',
        transition: 'transform 0.2s, box-shadow 0.2s',
        '&:hover': {
          transform: 'translateY(-2px)',
          boxShadow: 3,
        },
      }}
      onClick={() => navigate(`/book/${item.id}/reader`)}
    >
      {/* 封面 */}
      <Box
        sx={{
          width: 80,
          height: 120,
          flexShrink: 0,
          overflow: 'hidden',
        }}
      >
        {showFallback ? (
          <Box
            sx={{
              width: '100%',
              height: '100%',
              bgcolor: coverColor,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              p: 1,
            }}
          >
            <Typography variant="h5" sx={{ color: 'rgba(255,255,255,0.9)', mb: 0.5 }}>
              📖
            </Typography>
            <Typography
              variant="caption"
              sx={{
                color: 'rgba(255,255,255,0.95)',
                textAlign: 'center',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                display: '-webkit-box',
                WebkitLineClamp: 3,
                WebkitBoxOrient: 'vertical',
                lineHeight: 1.2,
                px: 0.5,
              }}
            >
              {item.title}
            </Typography>
          </Box>
        ) : (
          <Box
            component="img"
            src={`/api${item.cover_url}`}
            alt={item.title}
            loading="lazy"
            sx={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
            }}
            onError={(e: React.SyntheticEvent<HTMLImageElement>) => {
              setImageError(true)
            }}
          />
        )}
      </Box>

      {/* 信息 */}
      <CardContent sx={{ flex: 1, p: 1.5, display: 'flex', flexDirection: 'column' }}>
        <Typography
          variant="body2"
          fontWeight="medium"
          sx={{
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
          }}
        >
          {item.title}
        </Typography>
        
        {item.author_name && (
          <Typography
            variant="caption"
            color="text.secondary"
            sx={{
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
            }}
          >
            {item.author_name}
          </Typography>
        )}

        <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5 }}>
          {item.library_name}
        </Typography>

        <Box sx={{ mt: 'auto', minWidth: 0 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
            <Typography variant="caption" color="text.secondary" sx={{ flexShrink: 0 }}>
              阅读进度
            </Typography>
            <Box sx={{ flex: 1, minWidth: 0 }}>
              <LinearProgress
                variant="determinate"
                value={progressPercent}
                sx={{ height: 4, borderRadius: 2 }}
              />
            </Box>
            <Typography variant="caption" color="primary" fontWeight="medium" sx={{ flexShrink: 0 }}>
              {progressPercent}%
            </Typography>
          </Box>
        </Box>
      </CardContent>
    </Card>
  )
}
