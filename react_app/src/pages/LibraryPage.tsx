import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Box, Typography, Grid, FormControl, InputLabel, Select, MenuItem,
  ToggleButtonGroup, ToggleButton, CircularProgress, Alert, Chip
} from '@mui/material'
import { ViewModule, ViewList, Sort } from '@mui/icons-material'
import api from '../services/api'
import { BookSummary, LibrarySummary } from '../types'
import BookCard from '../components/BookCard'

interface BookResponse {
  id: number
  title: string
  author_name: string | null
  file_format: string
  file_size: number
  added_at: string
}

export default function LibraryPage() {
  const { libraryId } = useParams()
  const navigate = useNavigate()
  
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [libraries, setLibraries] = useState<LibrarySummary[]>([])
  const [books, setBooks] = useState<BookSummary[]>([])
  const [selectedLibrary, setSelectedLibrary] = useState<number | ''>('')
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [sortBy, setSortBy] = useState('added_at')

  useEffect(() => {
    loadLibraries()
  }, [])

  useEffect(() => {
    if (libraryId) {
      setSelectedLibrary(parseInt(libraryId))
    }
  }, [libraryId])

  useEffect(() => {
    loadBooks()
  }, [selectedLibrary])

  const loadLibraries = async () => {
    try {
      const response = await api.get<LibrarySummary[]>('/api/libraries')
      setLibraries(response.data)
    } catch (err) {
      console.error('加载书库失败:', err)
    }
  }

  const loadBooks = async () => {
    try {
      setLoading(true)
      setError('')
      
      let url = '/api/books?limit=100'
      if (selectedLibrary) {
        url += `&library_id=${selectedLibrary}`
      }
      
      const response = await api.get<BookResponse[]>(url)
      
      // 转换为 BookSummary 格式
      const bookSummaries: BookSummary[] = response.data.map((book) => ({
        id: book.id,
        title: book.title,
        author_name: book.author_name,
        cover_url: `/books/${book.id}/cover`,
        is_new: false,
        added_at: book.added_at,
        file_format: book.file_format,
      }))
      
      setBooks(bookSummaries)
    } catch (err) {
      console.error('加载书籍失败:', err)
      setError('加载失败，请刷新重试')
    } finally {
      setLoading(false)
    }
  }

  const handleLibraryChange = (newLibraryId: number | '') => {
    setSelectedLibrary(newLibraryId)
    if (newLibraryId) {
      navigate(`/library/${newLibraryId}`)
    } else {
      navigate('/library')
    }
  }

  // 排序书籍
  const sortedBooks = [...books].sort((a, b) => {
    switch (sortBy) {
      case 'title':
        return (a.title || '').localeCompare(b.title || '')
      case 'author':
        return (a.author_name || '').localeCompare(b.author_name || '')
      case 'added_at':
      default:
        return new Date(b.added_at || 0).getTime() - new Date(a.added_at || 0).getTime()
    }
  })

  const currentLibrary = libraries.find((lib) => lib.id === selectedLibrary)

  return (
    <Box sx={{ p: 3 }}>
      {/* 标题和工具栏 */}
      <Box sx={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: 2, mb: 3 }}>
        <Typography variant="h5" fontWeight="bold" sx={{ flexGrow: 1 }}>
          {currentLibrary?.name || '所有书籍'}
        </Typography>
        
        {/* 书库选择 */}
        <FormControl size="small" sx={{ minWidth: 150 }}>
          <InputLabel>书库</InputLabel>
          <Select
            value={selectedLibrary}
            label="书库"
            onChange={(e) => handleLibraryChange(e.target.value as number | '')}
          >
            <MenuItem value="">所有书库</MenuItem>
            {libraries.map((lib) => (
              <MenuItem key={lib.id} value={lib.id}>
                {lib.name} ({lib.book_count})
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        {/* 排序 */}
        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel>排序</InputLabel>
          <Select
            value={sortBy}
            label="排序"
            onChange={(e) => setSortBy(e.target.value)}
          >
            <MenuItem value="added_at">最新添加</MenuItem>
            <MenuItem value="title">按标题</MenuItem>
            <MenuItem value="author">按作者</MenuItem>
          </Select>
        </FormControl>

        {/* 视图切换 */}
        <ToggleButtonGroup
          value={viewMode}
          exclusive
          onChange={(_, value) => value && setViewMode(value)}
          size="small"
        >
          <ToggleButton value="grid">
            <ViewModule />
          </ToggleButton>
          <ToggleButton value="list">
            <ViewList />
          </ToggleButton>
        </ToggleButtonGroup>
      </Box>

      {/* 统计信息 */}
      <Box sx={{ mb: 3 }}>
        <Chip
          label={`共 ${books.length} 本书`}
          variant="outlined"
          size="small"
        />
      </Box>

      {/* 错误提示 */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* 加载状态 */}
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress />
        </Box>
      ) : books.length === 0 ? (
        <Box sx={{ textAlign: 'center', py: 8 }}>
          <Typography color="text.secondary">暂无书籍</Typography>
        </Box>
      ) : viewMode === 'grid' ? (
        /* 网格视图 */
        <Grid container spacing={2}>
          {sortedBooks.map((book) => (
            <Grid item xs={6} sm={4} md={3} lg={2} key={book.id}>
              <BookCard book={book} />
            </Grid>
          ))}
        </Grid>
      ) : (
        /* 列表视图 */
        <Box>
          {sortedBooks.map((book) => (
            <Box
              key={book.id}
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 2,
                p: 2,
                borderBottom: 1,
                borderColor: 'divider',
                cursor: 'pointer',
                '&:hover': { bgcolor: 'action.hover' },
              }}
              onClick={() => navigate(`/book/${book.id}`)}
            >
              {/* 封面缩略图 */}
              <Box
                sx={{
                  width: 48,
                  height: 72,
                  bgcolor: 'grey.800',
                  borderRadius: 1,
                  overflow: 'hidden',
                  flexShrink: 0,
                }}
              >
                {book.cover_url && (
                  <Box
                    component="img"
                    src={`/api${book.cover_url}`}
                    alt={book.title}
                    sx={{ width: '100%', height: '100%', objectFit: 'cover' }}
                    onError={(e: React.SyntheticEvent<HTMLImageElement>) => {
                      e.currentTarget.style.display = 'none'
                    }}
                  />
                )}
              </Box>

              {/* 信息 */}
              <Box sx={{ flex: 1, minWidth: 0 }}>
                <Typography variant="body1" fontWeight="medium" noWrap>
                  {book.title}
                </Typography>
                <Typography variant="body2" color="text.secondary" noWrap>
                  {book.author_name || '未知作者'}
                </Typography>
              </Box>

              {/* 格式标签 */}
              {book.file_format && (
                <Chip
                  label={book.file_format.toUpperCase()}
                  size="small"
                  sx={{ flexShrink: 0 }}
                />
              )}
            </Box>
          ))}
        </Box>
      )}
    </Box>
  )
}
