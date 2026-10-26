// 夹具：客户端白名单本身是干净的（不含 owner_id）——问题不在客户端
const ACTIVITY_FIELDS =
  'id, slug, title, cover_path'

async function listActivities() {
  return cloud.database
    .from('activities')
    .select(ACTIVITY_FIELDS)
    .order('starts_at', { ascending: true })
}
