# 在此目录创建 ark_key.txt，内容为火山方舟 ARK_API_KEY（单行）。
# 该文件通过 compose 的文件 secret 只读挂载到容器 /run/secrets/ark_key。
# 切勿提交真实密钥：建议在 .gitignore 中忽略 secrets/ark_key.txt。
