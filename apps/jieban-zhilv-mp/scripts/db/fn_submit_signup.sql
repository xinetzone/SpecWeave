CREATE OR REPLACE FUNCTION public.submit_signup(
  p_activity_id  BIGINT,
  p_companions   INTEGER,
  p_contact      TEXT,
  p_remark       TEXT,
  p_owner_name   TEXT,
  p_cover_path   TEXT DEFAULT NULL
)
RETURNS SETOF public.registrations
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path TO 'public'
AS $fn$
DECLARE
  v_activity public.activities;
  v_taken    BIGINT;
  v_row      public.registrations;
  v_uid      TEXT;
  v_scope    TEXT;
  v_owner    TEXT;
  v_dir      TEXT;
  v_file     TEXT;
BEGIN
  v_uid := auth.uid();
  IF v_uid IS NULL OR v_uid = '' THEN
    RAISE EXCEPTION '请先完成微信授权登录' USING ERRCODE = '42501';
  END IF;

  IF p_companions IS NULL OR p_companions < 1 OR p_companions > 4 THEN
    RAISE EXCEPTION '同行人数需在 1 到 4 之间' USING ERRCODE = '22023';
  END IF;

  IF p_contact IS NULL OR p_contact !~ '^1[0-9]{10}$' THEN
    RAISE EXCEPTION '手机号格式不正确' USING ERRCODE = '22023';
  END IF;

  IF p_remark IS NOT NULL AND length(p_remark) > 100 THEN
    RAISE EXCEPTION '备注不能超过 100 字' USING ERRCODE = '22023';
  END IF;

  IF p_owner_name IS NOT NULL AND length(p_owner_name) > 40 THEN
    RAISE EXCEPTION '称呼不能超过 40 字' USING ERRCODE = '22023';
  END IF;

  -- 配图路径校验：按 '/' 结构化分段比较，不把 uid 拼进正则模式。
  -- 期望形状 users/<本人 uid>/registrations/<文件名>，文件名内不再允许斜杠，
  -- 且扩展名限 png/jpg/jpeg。正则只作用在「值」上（文件名），不作为模式拼接。
  IF p_cover_path IS NOT NULL THEN
    v_scope := split_part(p_cover_path, '/', 1);
    v_owner := split_part(p_cover_path, '/', 2);
    v_dir   := split_part(p_cover_path, '/', 3);
    v_file  := split_part(p_cover_path, '/', 4);
    IF array_length(string_to_array(p_cover_path, '/'), 1) IS DISTINCT FROM 4
       OR v_scope IS DISTINCT FROM 'users'
       OR v_owner IS DISTINCT FROM v_uid
       OR v_dir IS DISTINCT FROM 'registrations'
       OR v_file !~ '^[A-Za-z0-9._-]+\.(jpg|jpeg|png)$' THEN
      RAISE EXCEPTION '配图路径不合法' USING ERRCODE = '22023';
    END IF;
  END IF;

  SELECT * INTO v_activity FROM public.activities
    WHERE id = p_activity_id FOR UPDATE;
  IF NOT FOUND THEN
    RAISE EXCEPTION '活动不存在或已下架' USING ERRCODE = 'P0002';
  END IF;

  IF NOT v_activity.published THEN
    RAISE EXCEPTION '活动不存在或已下架' USING ERRCODE = 'P0002';
  END IF;

  IF v_activity.starts_at IS NOT NULL AND v_activity.starts_at <= now() THEN
    RAISE EXCEPTION '活动已开始，报名通道已关闭' USING ERRCODE = 'P0001';
  END IF;

  SELECT COALESCE(sum(r.companions), 0)::BIGINT INTO v_taken
    FROM public.registrations r
    WHERE r.activity_id = p_activity_id AND r.status = 'confirmed';

  IF v_activity.capacity > 0 AND v_taken + p_companions > v_activity.capacity THEN
    RAISE EXCEPTION '名额已满' USING ERRCODE = 'P0001';
  END IF;

  INSERT INTO public.registrations (activity_id, companions, contact, remark, owner_name, cover_path)
  VALUES (p_activity_id, p_companions, p_contact, p_remark, p_owner_name, p_cover_path)
  RETURNING * INTO v_row;

  RETURN NEXT v_row;
EXCEPTION
  WHEN unique_violation THEN
    RAISE EXCEPTION '你已报名该活动' USING ERRCODE = '23505';
END;
$fn$;
