import { useState, useEffect } from 'react';
import { Box, CircularProgress, Typography } from '@mui/material';
import api from '../../services/api';

interface ComicImage {
  filename: string;
  size: number;
}

interface ComicReaderProps {
  bookId: string;
  images: ComicImage[];
  currentPage: number;
  onPageLoad: (index: number) => void;
  width?: number;
}

export default function ComicReader({ bookId, images, currentPage, onPageLoad, width }: ComicReaderProps) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [imageUrl, setImageUrl] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    const loadPage = async () => {
      if (currentPage < 0 || currentPage >= images.length) return;
      
      setLoading(true);
      setError(false);
      
      try {
        const response = await api.get(`/api/books/${bookId}/comic/page/${currentPage}`, {
          responseType: 'blob'
        });
        
        const url = URL.createObjectURL(response.data);
        if (mounted) {
          setImageUrl(url);
          setLoading(false);
          onPageLoad(currentPage);
        }
      } catch (err) {
        console.error('加载图片失败:', err);
        if (mounted) {
          setError(true);
          setLoading(false);
        }
      }
    };
    
    loadPage();
    
    return () => {
      mounted = false;
      if (imageUrl) URL.revokeObjectURL(imageUrl);
    };
  }, [bookId, currentPage, images]);

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', minHeight: '100vh', justifyContent: 'center' }}>
      {loading && (
        <Box sx={{ p: 4 }}>
          <CircularProgress />
        </Box>
      )}
      
      {error && (
        <Box sx={{ p: 4, textAlign: 'center' }}>
          <Typography color="error">加载图片失败</Typography>
        </Box>
      )}
      
      {imageUrl && !loading && !error && (
        <img 
          src={imageUrl} 
          alt={`Page ${currentPage + 1}`}
          style={{ 
            maxWidth: '100%', 
            maxHeight: '100vh', 
            objectFit: 'contain',
            width: width ? `${width}px` : 'auto'
          }}
        />
      )}
      
      <Typography variant="caption" sx={{ mt: 2, mb: 4, color: 'text.secondary' }}>
        第 {currentPage + 1} / {images.length} 页
      </Typography>
    </Box>
  );
}
