# 启用 GitHub Actions

目录附有工作流模板 [catalog.yml](catalog.yml)。启用后会在推送和 PR 中检查资源格式、生成一致性与目录测试。

将模板复制至 `.github/workflows/catalog.yml`，使用可写入 GitHub Actions 工作流的凭据提交即可。OAuth/Classic PAT 通常需要 `workflow` 权限；应按自己的凭据类型核对授权。本仓库初版将配置保留为模板，尚未启用线上工作流。

```bash
mkdir -p .github/workflows
cp docs/automation/catalog.yml .github/workflows/catalog.yml
git add .github/workflows/catalog.yml
git commit -m "Enable catalog checks"
git push
```

在启用之前也可以本地运行同样的检查：

```bash
python3 scripts/catalog.py --check
python3 -m unittest discover -s tests -v
```
