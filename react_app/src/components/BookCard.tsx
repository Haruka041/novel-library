import { Box, Card, CardContent, Typography, Skeleton, Chip } from '@mui/material'
import { useNavigate } from 'react-router-dom'
import { BookSummary } from '../types'

interface BookCardProps {
  book?: BookSummary
  loading?: boolean
  onClick?: () => void
}

export default function BookCard({ book, loading = false, onClick }: BookCardProps) {
  const navigate = useNavigate()

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
          bgcolor: 'grey.800',
          overflow: 'hidden',
        }}
      >
        {book.cover_url ? (
          <Box
            component="img"
            src={`/api${book.cover_url}`}
            alt={book.title}
            sx={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
            }}
            onError={(e: React.SyntheticEvent<HTMLImageElement>) => {
              e.currentTarget.style.display = 'none'
            }}
          />
        ) : (
          <Box
            sx={{
              width: '100%',
              height: '100%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              bgcolor: 'grey.700',
            }}
          >
            <Typography variant="h4" color="grey.500">
              📖
            </Typography>
          </Box>
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
