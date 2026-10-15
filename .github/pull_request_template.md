## 改动

说明新增或修改的资源 ID，以及范围、访问或许可变化。

## 核实依据

列出官方说明、发布记录或 DOI；说明未核对或有冲突的内容。

## 检查

- [ ] 资源信息修改于 `data/resources.json`，已重新生成导航、卡片和 CSV
- [ ] `python3 scripts/catalog.py --check`
- [ ] `python3 -m unittest discover -s tests -v`
- [ ] 未提交原始大文件、凭据或临时签名链接
