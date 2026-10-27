CREATE OR REPLACE FUNCTION public.cancel_registration(p_registration_id BIGINT)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path TO 'public'
AS $fn$
DECLARE
  v_uid TEXT;
  v_hit INTEGER;
BEGIN
  v_uid := auth.uid();
  IF v_uid IS NULL OR v_uid = '' THEN
    RAISE EXCEPTION '请先完成微信授权登录' USING ERRCODE = '42501';
  END IF;

  UPDATE public.registrations
    SET status = 'cancelled'
    WHERE id = p_registration_id AND owner_id = v_uid AND status = 'confirmed';

  GET DIAGNOSTICS v_hit = ROW_COUNT;
  RETURN v_hit > 0;
END;
$fn$;
