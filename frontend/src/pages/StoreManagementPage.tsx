import { useState, useEffect } from 'react'
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  TextField,
  Button,
  Grid,
  Alert,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material'
import {
  Store as StoreIcon,
  Add,
  Edit,
  Delete,
  Save,
  Cancel,
} from '@mui/icons-material'
import { storeApi } from '@services/api'

interface Store {
  id: number
  name: string
  address?: string
  phone?: string
  open_time?: string
  close_time?: string
  created_at: string
  updated_at: string
}

function StoreManagementPage() {
  // State
  const [stores, setStores] = useState<Store[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  // 새 매장 등록 폼
  const [newStore, setNewStore] = useState({
    name: '',
    address: '',
    phone: '',
    open_time: '',
    close_time: '',
  })

  // 수정 모드
  const [editingStore, setEditingStore] = useState<Store | null>(null)
  const [editDialogOpen, setEditDialogOpen] = useState(false)

  // 매장 목록 조회
  const loadStores = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const response = await storeApi.getStores()
      setStores(response.data.stores)
    } catch (err: any) {
      setError(err.message || '매장 목록 조회 중 오류가 발생했습니다.')
    } finally {
      setIsLoading(false)
    }
  }

  // 초기 로드
  useEffect(() => {
    loadStores()
  }, [])

  // 새 매장 등록
  const handleCreateStore = async () => {
    if (!newStore.name.trim()) {
      setError('매장 이름을 입력해주세요.')
      return
    }

    setIsLoading(true)
    setError(null)
    setSuccess(null)

    try {
      await storeApi.createStore({
        name: newStore.name,
        address: newStore.address || undefined,
        phone: newStore.phone || undefined,
        open_time: newStore.open_time || undefined,
        close_time: newStore.close_time || undefined,
      })

      setSuccess('매장이 성공적으로 등록되었습니다.')
      setNewStore({
        name: '',
        address: '',
        phone: '',
        open_time: '',
        close_time: '',
      })

      // 목록 다시 로드
      await loadStores()
    } catch (err: any) {
      setError(err.message || '매장 등록 중 오류가 발생했습니다.')
    } finally {
      setIsLoading(false)
    }
  }

  // 매장 수정
  const handleUpdateStore = async () => {
    if (!editingStore) return

    setIsLoading(true)
    setError(null)

    try {
      await storeApi.updateStore(editingStore.id, {
        name: editingStore.name,
        address: editingStore.address || undefined,
        phone: editingStore.phone || undefined,
        open_time: editingStore.open_time || undefined,
        close_time: editingStore.close_time || undefined,
      })

      setSuccess('매장 정보가 성공적으로 수정되었습니다.')
      setEditDialogOpen(false)
      setEditingStore(null)

      // 목록 다시 로드
      await loadStores()
    } catch (err: any) {
      setError(err.message || '매장 수정 중 오류가 발생했습니다.')
    } finally {
      setIsLoading(false)
    }
  }

  // 매장 삭제
  const handleDeleteStore = async (storeId: number, storeName: string) => {
    if (!confirm(`"${storeName}" 매장을 삭제하시겠습니까?\n매장의 모든 메뉴도 함께 삭제됩니다.`)) {
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      await storeApi.deleteStore(storeId)
      setSuccess('매장이 성공적으로 삭제되었습니다.')

      // 목록 다시 로드
      await loadStores()
    } catch (err: any) {
      setError(err.message || '매장 삭제 중 오류가 발생했습니다.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* 헤더 */}
      <Box sx={{ mb: 4, textAlign: 'center' }}>
        <StoreIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
        <Typography variant="h3" gutterBottom fontWeight="bold">
          매장 관리
        </Typography>
        <Typography variant="h6" color="text.secondary">
          매장을 등록하고 관리합니다
        </Typography>
      </Box>

      {/* 에러 메시지 */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* 성공 메시지 */}
      {success && (
        <Alert severity="success" sx={{ mb: 3 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}

      {/* 새 매장 등록 */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            새 매장 등록
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="매장 이름 *"
                value={newStore.name}
                onChange={(e) => setNewStore({ ...newStore, name: e.target.value })}
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="주소"
                value={newStore.address}
                onChange={(e) => setNewStore({ ...newStore, address: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="전화번호"
                value={newStore.phone}
                onChange={(e) => setNewStore({ ...newStore, phone: e.target.value })}
                placeholder="02-1234-5678"
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="오픈 시간"
                type="time"
                value={newStore.open_time}
                onChange={(e) => setNewStore({ ...newStore, open_time: e.target.value })}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="마감 시간"
                type="time"
                value={newStore.close_time}
                onChange={(e) => setNewStore({ ...newStore, close_time: e.target.value })}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12}>
              <Button
                variant="contained"
                size="large"
                fullWidth
                onClick={handleCreateStore}
                disabled={isLoading || !newStore.name.trim()}
                startIcon={isLoading ? <CircularProgress size={20} /> : <Add />}
              >
                {isLoading ? '등록 중...' : '매장 등록'}
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* 매장 목록 */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            등록된 매장 목록 ({stores.length}개)
          </Typography>

          {isLoading && stores.length === 0 ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress />
            </Box>
          ) : stores.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Typography color="text.secondary">
                등록된 매장이 없습니다. 새 매장을 등록해주세요.
              </Typography>
            </Box>
          ) : (
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>ID</TableCell>
                    <TableCell>매장 이름</TableCell>
                    <TableCell>주소</TableCell>
                    <TableCell>전화번호</TableCell>
                    <TableCell>영업 시간</TableCell>
                    <TableCell align="center">작업</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {stores.map((store) => (
                    <TableRow key={store.id}>
                      <TableCell>{store.id}</TableCell>
                      <TableCell>{store.name}</TableCell>
                      <TableCell>{store.address || '-'}</TableCell>
                      <TableCell>{store.phone || '-'}</TableCell>
                      <TableCell>
                        {store.open_time && store.close_time
                          ? `${store.open_time} ~ ${store.close_time}`
                          : '-'}
                      </TableCell>
                      <TableCell align="center">
                        <IconButton
                          size="small"
                          color="primary"
                          onClick={() => {
                            setEditingStore(store)
                            setEditDialogOpen(true)
                          }}
                          title="수정"
                        >
                          <Edit />
                        </IconButton>
                        <IconButton
                          size="small"
                          color="error"
                          onClick={() => handleDeleteStore(store.id, store.name)}
                          title="삭제"
                        >
                          <Delete />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>

      {/* 수정 다이얼로그 */}
      <Dialog
        open={editDialogOpen}
        onClose={() => {
          setEditDialogOpen(false)
          setEditingStore(null)
        }}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>매장 정보 수정</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="매장 이름 *"
                value={editingStore?.name || ''}
                onChange={(e) =>
                  setEditingStore(editingStore ? { ...editingStore, name: e.target.value } : null)
                }
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="주소"
                value={editingStore?.address || ''}
                onChange={(e) =>
                  setEditingStore(
                    editingStore ? { ...editingStore, address: e.target.value } : null
                  )
                }
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="전화번호"
                value={editingStore?.phone || ''}
                onChange={(e) =>
                  setEditingStore(editingStore ? { ...editingStore, phone: e.target.value } : null)
                }
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <TextField
                fullWidth
                label="오픈 시간"
                type="time"
                value={editingStore?.open_time || ''}
                onChange={(e) =>
                  setEditingStore(
                    editingStore ? { ...editingStore, open_time: e.target.value } : null
                  )
                }
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <TextField
                fullWidth
                label="마감 시간"
                type="time"
                value={editingStore?.close_time || ''}
                onChange={(e) =>
                  setEditingStore(
                    editingStore ? { ...editingStore, close_time: e.target.value } : null
                  )
                }
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => {
              setEditDialogOpen(false)
              setEditingStore(null)
            }}
            startIcon={<Cancel />}
          >
            취소
          </Button>
          <Button
            onClick={handleUpdateStore}
            variant="contained"
            disabled={isLoading || !editingStore?.name.trim()}
            startIcon={isLoading ? <CircularProgress size={20} /> : <Save />}
          >
            저장
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  )
}

export default StoreManagementPage
