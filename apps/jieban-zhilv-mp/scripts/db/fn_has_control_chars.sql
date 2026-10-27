-- 判断文本是否含控制字符（换行、制表符等）。
--
-- 长度检查挡不住控制字符：btrim 只去首尾空白，中间的 \n 会保留，
-- 而客户端按单行/紧凑布局渲染，含换行的标题会破坏排版。
--
-- 正则只用字面量模式，不拼接任何用户输入（uid 拼进正则会放宽校验）。
--
-- IMMUTABLE：纯函数，不读表不受 RLS 影响，可在 CHECK 与函数体内自由调用。
CREATE OR REPLACE FUNCTION public.has_control_chars(p_text TEXT)
RETURNS BOOLEAN
LANGUAGE sql
IMMUTABLE
AS $$
  SELECT p_text IS NOT NULL AND p_text ~ '[\x00-\x1F\x7F]';
$$;
