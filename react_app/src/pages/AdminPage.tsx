import { useState } from 'react'
import { Box, Tabs, Tab, Typography, Container } from '@mui/material'
import { People, LibraryBooks, Backup, Image, TextFields } from '@mui/icons-material'
import UsersTab from '../components/admin/UsersTab'
import LibrariesTab from '../components/admin/LibrariesTab'
import BackupTab from '../components/admin/BackupTab'
import CoversTab from '../components/admin/CoversTab'
import FontsTab from '../components/admin/FontsTab'

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props
  return (
    <div role="tabpanel" hidden={value !== index} {...other}>
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  )
}

export default function AdminPage() {
  const [tabValue, setTabValue] = useState(0)

  return (
    <Container maxWidth="lg" sx={{ py: 3 }}>
      <Typography variant="h5" fontWeight="bold" sx={{ mb: 3 }}>
        后台管理
      </Typography>

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
        <Tabs
          value={tabValue}
          onChange={(_, v) => setTabValue(v)}
          variant="scrollable"
          scrollButtons="auto"
        >
          <Tab icon={<People />} label="用户管理" iconPosition="start" />
          <Tab icon={<LibraryBooks />} label="书库管理" iconPosition="start" />
          <Tab icon={<Backup />} label="备份管理" iconPosition="start" />
          <Tab icon={<Image />} label="封面管理" iconPosition="start" />
          <Tab icon={<TextFields />} label="字体管理" iconPosition="start" />
        </Tabs>
      </Box>

      <TabPanel value={tabValue} index={0}>
        <UsersTab />
      </TabPanel>
      <TabPanel value={tabValue} index={1}>
        <LibrariesTab />
      </TabPanel>
      <TabPanel value={tabValue} index={2}>
        <BackupTab />
      </TabPanel>
      <TabPanel value={tabValue} index={3}>
        <CoversTab />
      </TabPanel>
      <TabPanel value={tabValue} index={4}>
        <FontsTab />
      </TabPanel>
    </Container>
  )
}
