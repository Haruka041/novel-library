// 书籍摘要
export interface BookSummary {
  id: number
  title: string
  author_name: string | null
  cover_url: string | null
  is_new: boolean
  added_at: string | null
  file_format: string | null
}

// 书库摘要
export interface LibrarySummary {
  id: number
  name: string
  book_count: number
  cover_url: string | null
}

// 继续阅读项
export interface ContinueReadingItem {
  id: number
  title: string
  author_name: string | null
  cover_url: string | null
  progress: number
  last_read_at: string
  library_id: number
  library_name: string
}

// 书库最新书籍
export interface LibraryLatest {
  library_id: number
  library_name: string
  books: BookSummary[]
}

// Dashboard 响应
export interface DashboardResponse {
  continue_reading: ContinueReadingItem[]
  libraries: LibrarySummary[]
  latest_by_library: LibraryLatest[]
  favorites_count: number
}

// 书籍详情
export interface Book {
  id: number
  title: string
  author_name: string | null
  description: string | null
  cover_url: string | null
  file_format: string | null
  file_size: number | null
  library_id: number
  library_name: string | null
  added_at: string | null
  is_favorite: boolean
}

// 书籍列表响应
export interface BooksResponse {
  items: BookSummary[]
  total: number
  page: number
  page_size: number
}

// 用户信息
export interface User {
  id: number
  username: string
  email?: string
  is_admin: boolean
}
