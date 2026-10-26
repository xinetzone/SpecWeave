// 夹具：客户端字段白名单含 owner_id
const ACTIVITY_FIELDS =
  'id, slug, title, summary, cover_path, owner_id'

async function listActivities() {
  return cloud.database
    .from('activities')
    .select(ACTIVITY_FIELDS)
    .order('starts_at', { ascending: true })
}
