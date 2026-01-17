import { useState, useEffect, useRef, useCallback, useMemo } from 'react'
import { useParams, useNavigate, useSearchParams } from 'react-router-dom'
import {
  Box, Typography, Grid, FormControl, InputLabel, Select, MenuItem,
  ToggleButtonGroup, ToggleButton, CircularProgress, Alert, Chip, Menu,
  Button, Collapse, Autocomplete, TextField, Stack
} from '@mui/material'
import { ViewModule, ViewList, PhotoSizeSelectLarge, FilterList, ExpandMore, ExpandLess } from '@mui/icons-material'
import api from '../services/api'
import { BookSummary, LibrarySummary } from '../types'
import BookCard from '../components/BookCard'
import Pagination from '../components/Pagination'
import { useSettingsStore } from '../stores/settingsStore'
import { useDocumentTitle } from '../hooks/useDocumentTitle'

interface TagInfo {
  id: number
  name: string
  type: string
  book_count?: number
}

interface BookResponse {
  id: number
  title: string
  author_name: string | null
  file_format: string
  file_size: number
  added_at: string
}

interface BooksApiResponse {
  books: BookResponse[]
  total: number
  page: number
  limit: number
  total_pages: number
}

// 支持的格式列表
const SUPPORTED_FORMATS = ['txt', 'epub', 'mobi', 'azw', 'azw3', 'pdf']

export default function LibraryPage() {
  const { libraryId } = useParams()
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()
  const { coverSize, setCoverSize, paginationMode } = useSettingsStore()
  
  // 从 URL 参数中读取状态
  const urlPage = parseInt(searchParams.get('page') || '1', 10)
  const urlTags = useMemo(() => {
    const tagStr = searchParams.get('tags')
    if (!tagStr) return [] as number[]
    return tagStr.split(',').map(t => parseInt(t, 10)).filter(n => !isNaN(n))
  }, [searchParams])
  const urlFormats = useMemo(() => {
    const formatStr = searchParams.get('formats')
    if (!formatStr) return [] as string[]
    return formatStr.split(',').filter(Boolean)
  }, [searchParams])
  const urlSort = searchParams.get('sort') || 'added_at_desc'
  const urlView = searchParams.get('view') as 'grid' | 'list' || 'grid'
  
  const [loading, setLoading] = useState(true)
  const [loadingMore, setLoadingMore] = useState(false)
  const [error, setError] = useState('')
  const [libraries, setLibraries] = useState<LibrarySummary[]>([])
  const [books, setBooks] = useState<BookSummary[]>([])
  const [selectedLibrary, setSelectedLibrary] = useState<number | ''>('')
  const [viewMode, setViewMode] = useState<'grid' | 'list'>(urlView)
  const [sortBy, setSortBy] = useState(urlSort)
  const [page, setPage] = useState(urlPage)
  const [totalPages, setTotalPages] = useState(0)
  const [hasMore, setHasMore] = useState(true)
  const [totalCount, setTotalCount] = useState(0)
  const [sizeMenuAnchor, setSizeMenuAnchor] = useState<null | HTMLElement>(null)
  const observerTarget = useRef<HTMLDivElement>(null)
  
  // 筛选器状态
  const [showFilters, setShowFilters] = useState(false)
  const [allTags, setAllTags] = useState<TagInfo[]>([])
  const [selectedTags, setSelectedTags] = useState<TagInfo[]>([])
  const [selectedFormats, setSelectedFormats] = useState<string[]>(urlFormats)

  // 更新 URL 参数的辅助函数
  const updateUrlParams = useCallback((updates: Record<string, string | number | null>) => {
    setSearchParams(prev => {
      const newParams = new URLSearchParams(prev)
      for (const [key, value] of Object.entries(updates)) {
        if (value === null || value === '' || value === undefined) {
          newParams.delete(key)
        } else {
          newParams.set(key, String(value))
        }
      }
      return newParams
    }, { replace: true })
  }, [setSearchParams])

  useEffect(() => {
    loadLibraries()
  }, [])

  useEffect(() => {
    if (libraryId) {
      setSelectedLibrary(parseInt(libraryId))
    }
  }, [libraryId])

  // 书库变化时重新加载标签
  useEffect(() => {
    loadTags()
  }, [selectedLibrary])

  // 当 allTags 加载完成后，根据 URL 参数设置 selectedTags
  useEffect(() => {
    if (allTags.length > 0 && urlTags.length > 0) {
      const tagsFromUrl = allTags.filter(t => urlTags.includes(t.id))
      setSelectedTags(tagsFromUrl)
    } else if (urlTags.length === 0) {
      setSelectedTags([])
    }
  }, [allTags, urlTags])

  // URL 参数变化时触发加载
  useEffect(() => {
    setPage(urlPage)
    setHasMore(true)
    setBooks([])
    loadBooks(urlPage, false)
  }, [selectedLibrary, urlTags.join(','), urlFormats.join(','), urlPage, paginationMode])

  // 加载标签列表（根据选中的书库）
  const loadTags = async () => {
    try {
      let url: string
      if (selectedLibrary) {
        url = `/api/tags/library/${selectedLibrary}`
      } else {
        url = '/api/tags/all-libraries'
      }
      const response = await api.get<TagInfo[]>(url)
      const tags = Array.isArray(response.data) ? response.data : []
      setAllTags(tags)
    } catch (err) {
      console.error('加载标签失败:', err)
      try {
        const response = await api.get<TagInfo[]>('/api/tags')
        const tags = Array.isArray(response.data) ? response.data : (response.data as any).tags || []
        setAllTags(tags)
      } catch (fallbackErr) {
        console.error('加载标签失败(fallback):', fallbackErr)
      }
    }
  }

  const loadLibraries = async () => {
    try {
      const response = await api.get<LibrarySummary[]>('/api/libraries')
      setLibraries(response.data)
    } catch (err) {
      console.error('加载书库失败:', err)
    }
  }

  const loadBooks = async (pageNum: number = 1, append: boolean = false) => {
    try {
      if (append) {
        setLoadingMore(true)
      } else {
        setLoading(true)
      }
      setError('')
      
      const limit = 50
      let url = `/api/books?page=${pageNum}&limit=${limit}`
      if (selectedLibrary) {
        url += `&library_id=${selectedLibrary}`
      }
      // 添加格式筛选
      if (urlFormats.length > 0) {
        url += `&formats=${urlFormats.join(',')}`
      }
      // 添加标签筛选
      if (urlTags.length > 0) {
        url += `&tag_ids=${urlTags.join(',')}`
      }
      // 添加排序参数
      if (sortBy) {
        url += `&sort=${sortBy}`
      }
      
      const response = await api.get<BooksApiResponse>(url)
      
      // 转换为 BookSummary 格式
      const bookSummaries: BookSummary[] = response.data.books.map((book) => ({
        id: book.id,
        title: book.title,
        author_name: book.author_name,
        cover_url: `/books/${book.id}/cover`,
        is_new: false,
        added_at: book.added_at,
        file_format: book.file_format,
      }))
      
      if (append) {
        setBooks(prev => [...prev, ...bookSummaries])
      } else {
        setBooks(bookSummaries)
      }
      
      setTotalCount(response.data.total)
      setTotalPages(response.data.total_pages)
      setHasMore(pageNum < response.data.total_pages)
    } catch (err) {
      console.error('加载书籍失败:', err)
      setError('加载失败，请刷新重试')
    } finally {
      setLoading(false)
      setLoadingMore(false)
    }
  }

  // 传统分页：切换页码
  const handlePageChange = (newPage: number) => {
    updateUrlParams({ page: newPage > 1 ? newPage : null })
    setPage(newPage)
    loadBooks(newPage, false)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  // 无限滚动：加载更多
  const loadMore = useCallback(() => {
    if (!loadingMore && hasMore) {
      const nextPage = page + 1
      setPage(nextPage)
      loadBooks(nextPage, true)
    }
  }, [page, loadingMore, hasMore])

  // 无限滚动观察器
  useEffect(() => {
    if (paginationMode !== 'infinite') return
    
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && hasMore && !loading && !loadingMore) {
          loadMore()
        }
      },
      { threshold: 0.1 }
    )
    
    if (observerTarget.current) {
      observer.observe(observerTarget.current)
    }
    
    return () => observer.disconnect()
  }, [loadMore, hasMore, loading, loadingMore, paginationMode])

  const handleLibraryChange = (newLibraryId: number | '') => {
    setSelectedLibrary(newLibraryId)
    // 切换书库时清除筛选参数
    if (newLibraryId) {
      navigate(`/library/${newLibraryId}`)
    } else {
      navigate('/library')
    }
  }

  // 处理标签选择变化
  const handleTagsChange = (newTags: TagInfo[]) => {
    setSelectedTags(newTags)
    const tagIds = newTags.map(t => t.id)
    updateUrlParams({ 
      tags: tagIds.length > 0 ? tagIds.join(',') : null,
      page: null  // 重置页码
    })
  }

  // 处理格式选择变化
  const handleFormatsChange = (format: string) => {
    let newFormats: string[]
    if (selectedFormats.includes(format)) {
      newFormats = selectedFormats.filter(f => f !== format)
    } else {
      newFormats = [...selectedFormats, format]
    }
    setSelectedFormats(newFormats)
    updateUrlParams({
      formats: newFormats.length > 0 ? newFormats.join(',') : null,
      page: null
    })
  }

  // 处理排序变化
  const handleSortChange = (newSort: string) => {
    setSortBy(newSort)
    updateUrlParams({ 
      sort: newSort !== 'added_at_desc' ? newSort : null,
      page: null  // 重置页码
    })
    // 立即重新加载
    setBooks([])
    setPage(1)
    loadBooks(1, false)
  }

  // 处理视图模式变化
  const handleViewChange = (newView: 'grid' | 'list') => {
    setViewMode(newView)
    updateUrlParams({ view: newView !== 'grid' ? newView : null })
  }

  // 清除所有筛选
  const clearFilters = () => {
    setSelectedTags([])
    setSelectedFormats([])
    updateUrlParams({ tags: null, formats: null, page: null })
  }

  // 计算当前有多少筛选条件
  const filterCount = selectedTags.length + selectedFormats.length

  // 根据封面尺寸计算网格列数
  const getGridColumns = () => {
    switch (coverSize) {
      case 'small':
        return { xs: 4, sm: 3, md: 2.4, lg: 2, xl: 1.5 }
      case 'medium':
        return { xs: 6, sm: 4, md: 3, lg: 2, xl: 2 }
      case 'large':
        return { xs: 6, sm: 4, md: 3, lg: 2.4, xl: 2 }
    }
  }

  const currentLibrary = libraries.find((lib) => lib.id === selectedLibrary)

  useDocumentTitle(currentLibrary?.name || '书库')

  const renderPagination = () => {
    if (paginationMode === 'traditional') {
      return totalPages > 0 && (
        <Pagination
          page={page}
          totalPages={totalPages}
          onPageChange={handlePageChange}
          disabled={loading}
        />
      )
    } else {
      return (
        <>
          <Box ref={observerTarget} sx={{ height: 20, mt: 4 }} />
          {loadingMore && (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress size={32} />
            </Box>
          )}
          {!hasMore && books.length > 0 && (
            <Typography variant="body2" color="text.secondary" textAlign="center" sx={{ py: 4 }}>
              已加载全部书籍
            </Typography>
          )}
        </>
      )
    }
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* 标题和工具栏 */}
      <Box sx={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: 2, mb: 3 }}>
        <Typography variant="h5" fontWeight="bold" sx={{ flexGrow: 1 }}>
          {currentLibrary?.name || '所有书籍'}
        </Typography>
        
        {/* 筛选按钮 */}
        <Button
          variant={showFilters ? 'contained' : 'outlined'}
          size="small"
          startIcon={<FilterList />}
          endIcon={showFilters ? <ExpandLess /> : <ExpandMore />}
          onClick={() => setShowFilters(!showFilters)}
          color={filterCount > 0 ? 'primary' : 'inherit'}
        >
          筛选{filterCount > 0 ? ` (${filterCount})` : ''}
        </Button>
        
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
        <FormControl size="small" sx={{ minWidth: 140 }}>
          <InputLabel>排序</InputLabel>
          <Select
            value={sortBy}
            label="排序"
            onChange={(e) => handleSortChange(e.target.value)}
          >
            <MenuItem value="added_at_desc">最新添加</MenuItem>
            <MenuItem value="added_at_asc">最早添加</MenuItem>
            <MenuItem value="title_asc">标题 A-Z</MenuItem>
            <MenuItem value="title_desc">标题 Z-A</MenuItem>
            <MenuItem value="size_desc">大小↓</MenuItem>
            <MenuItem value="size_asc">大小↑</MenuItem>
            <MenuItem value="format_asc">格式 A-Z</MenuItem>
            <MenuItem value="format_desc">格式 Z-A</MenuItem>
            <MenuItem value="rating_asc">分级↑</MenuItem>
            <MenuItem value="rating_desc">分级↓</MenuItem>
          </Select>
        </FormControl>

        {/* 封面尺寸 */}
        <ToggleButton
          value="size"
          size="small"
          onClick={(e) => setSizeMenuAnchor(e.currentTarget)}
        >
          <PhotoSizeSelectLarge />
        </ToggleButton>
        <Menu
          anchorEl={sizeMenuAnchor}
          open={Boolean(sizeMenuAnchor)}
          onClose={() => setSizeMenuAnchor(null)}
        >
          <MenuItem
            selected={coverSize === 'small'}
            onClick={() => {
              setCoverSize('small')
              setSizeMenuAnchor(null)
            }}
          >
            小
          </MenuItem>
          <MenuItem
            selected={coverSize === 'medium'}
            onClick={() => {
              setCoverSize('medium')
              setSizeMenuAnchor(null)
            }}
          >
            中
          </MenuItem>
          <MenuItem
            selected={coverSize === 'large'}
            onClick={() => {
              setCoverSize('large')
              setSizeMenuAnchor(null)
            }}
          >
            大
          </MenuItem>
        </Menu>

        {/* 视图切换 */}
        <ToggleButtonGroup
          value={viewMode}
          exclusive
          onChange={(_, value) => value && handleViewChange(value)}
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

      {/* 筛选器面板 */}
      <Collapse in={showFilters}>
        <Box sx={{ mb: 3, p: 2, bgcolor: 'background.paper', borderRadius: 1, border: 1, borderColor: 'divider' }}>
          <Stack spacing={2}>
            {/* 格式筛选 */}
            <Box>
              <Typography variant="subtitle2" sx={{ mb: 1 }}>文件格式</Typography>
              <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                {SUPPORTED_FORMATS.map((format) => (
                  <Chip
                    key={format}
                    label={format.toUpperCase()}
                    onClick={() => handleFormatsChange(format)}
                    color={selectedFormats.includes(format) ? 'primary' : 'default'}
                    variant={selectedFormats.includes(format) ? 'filled' : 'outlined'}
                  />
                ))}
              </Stack>
            </Box>

            {/* 标签筛选 */}
            <Box>
              <Typography variant="subtitle2" sx={{ mb: 1 }}>标签</Typography>
              <Autocomplete
                multiple
                options={allTags}
                getOptionLabel={(option) => option.book_count !== undefined 
                  ? `${option.name} (${option.book_count})`
                  : option.name
                }
                value={selectedTags}
                onChange={(_, newValue) => handleTagsChange(newValue)}
                isOptionEqualToValue={(option, value) => option.id === value.id}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    placeholder="选择标签..."
                    size="small"
                  />
                )}
                renderOption={(props, option) => (
                  <li {...props} key={option.id}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', width: '100%' }}>
                      <span>{option.name}</span>
                      {option.book_count !== undefined && (
                        <Typography variant="body2" color="text.secondary" sx={{ ml: 2 }}>
                          {option.book_count}
                        </Typography>
                      )}
                    </Box>
                  </li>
                )}
                renderTags={(value, getTagProps) =>
                  value.map((option, index) => (
                    <Chip
                      label={option.name}
                      size="small"
                      {...getTagProps({ index })}
                      key={option.id}
                    />
                  ))
                }
              />
            </Box>

            {/* 清除筛选按钮 */}
            {filterCount > 0 && (
              <Box>
                <Button size="small" onClick={clearFilters}>
                  清除所有筛选
                </Button>
              </Box>
            )}
          </Stack>
        </Box>
      </Collapse>

      {/* 统计信息 */}
      <Box sx={{ mb: 3, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
        <Chip
          label={`共 ${totalCount} 本书`}
          variant="outlined"
          size="small"
        />
        {paginationMode === 'traditional' && totalPages > 0 && (
          <Chip
            label={`第 ${page} 页 / 共 ${totalPages} 页`}
            size="small"
            color="primary"
            variant="outlined"
          />
        )}
        {paginationMode === 'infinite' && books.length > 0 && books.length < totalCount && (
          <Chip
            label={`已加载 ${books.length}`}
            size="small"
            color="primary"
            variant="outlined"
          />
        )}
        {loadingMore && (
          <Chip
            label="加载中..."
            size="small"
            color="primary"
            variant="outlined"
          />
        )}
        {/* 显示当前筛选条件 */}
        {selectedFormats.map(format => (
          <Chip
            key={format}
            label={`格式: ${format.toUpperCase()}`}
            size="small"
            color="secondary"
            onDelete={() => handleFormatsChange(format)}
          />
        ))}
        {selectedTags.map(tag => (
          <Chip
            key={tag.id}
            label={`标签: ${tag.name}`}
            size="small"
            color="secondary"
            onDelete={() => handleTagsChange(selectedTags.filter(t => t.id !== tag.id))}
          />
        ))}
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
          <Typography color="text.secondary">
            {filterCount > 0 ? '没有符合筛选条件的书籍' : '暂无书籍'}
          </Typography>
          {filterCount > 0 && (
            <Button sx={{ mt: 2 }} onClick={clearFilters}>
              清除筛选条件
            </Button>
          )}
        </Box>
      ) : viewMode === 'grid' ? (
        <>
          <Grid container spacing={2}>
            {books.map((book) => (
              <Grid item {...getGridColumns()} key={book.id}>
                <BookCard book={book} />
              </Grid>
            ))}
          </Grid>
          {renderPagination()}
        </>
      ) : (
        <>
          <Box>
            {books.map((book) => (
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

                <Box sx={{ flex: 1, minWidth: 0 }}>
                  <Typography variant="body1" fontWeight="medium" noWrap>
                    {book.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" noWrap>
                    {book.author_name || '未知作者'}
                  </Typography>
                </Box>

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
          {renderPagination()}
        </>
      )}
    </Box>
  )
}
