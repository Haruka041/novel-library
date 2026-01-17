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

// 书籍组
export interface BookGroup {
  id: number
  name: string | null
  primary_book_id: number | null
  created_at: string
}

// 书籍组中的书籍信息
export interface GroupedBook {
  id: number
  title: string
  author_name: string | null
  cover_path: string | null
  version_count: number
  formats: string[]
  total_size: number
  is_primary: boolean
  is_current: boolean
}

// 重复书籍检测中的书籍信息
export interface DuplicateBook {
  id: number
  title: string
  author_name: string | null
  version_count: number
  formats: string[]
  total_size: number
  added_at: string
  group_id: number | null
  is_group_primary: boolean
}

// 重复书籍分组
export interface DuplicateGroup {
  key: string
  books: DuplicateBook[]
  suggested_primary_id: number
  reason: string
}

// 重复检测响应
export interface DetectDuplicatesResponse {
  library_id: number
  library_name: string
  duplicate_group_count: number
  duplicate_groups: DuplicateGroup[]
}

// 书籍组创建请求
export interface GroupBooksRequest {
  primary_book_id: number
  book_ids: number[]
  group_name?: string
}

// 书籍组创建响应
export interface GroupBooksResponse {
  status: string
  group_id: number
  group_name: string
  primary_book_id: number
  book_count: number
  added_count: number
}

// 获取书籍组响应
export interface GetBookGroupResponse {
  book_id: number
  book_title: string
  group_id: number | null
  grouped_books: GroupedBook[]
  is_grouped: boolean
}
