---
keywords:
- Grafana
title: "Grafana 一个面板配置多数据源"
date: 2025-06-23T05:15:34Z
description: 使用 Mixed 数据源在同一个 Grafana 面板中配置不同来源的查询，说明结果合并、表格查看和分享权限的区别。
lastmod: 2026-10-31T14:00:00+08:00
draft: false
author: 小碗汤
hideToc: false
enableToc: true
enableTocContent: false
tocFolding: false
tocLevels: ["h2", "h3", "h4"]
tags:
- Grafana
categories: Grafana
img: https://images.kubeinfo.cn/uPic/202109151325055.png
---

原笔记参考了 [Grafana 官方的多数据源示例](https://grafana.com/blog/2024/11/07/how-to-work-with-multiple-data-sources-in-grafana-dashboards-best-practices-to-get-started/)。

原笔记使用的镜像为 `grafana:10.2.2`，这个版本支持混合数据源。

## 在同一个面板中配置多个数据源

Grafana 的 Mixed 数据源允许每条查询分别选择数据源。对照官方的数据源说明和多数据源示例，可以把配置过程拆成下面几步。下文保留原笔记的 10.2.2 版本背景，新版本的菜单名称可能不同。

1. 先在 Grafana 中配置要使用的数据源，并分别确认它们能返回查询结果。
2. 新建面板，或者打开现有面板的编辑界面。
3. 在 Queries 区域将面板的数据源切换为 `Mixed`。
4. 为查询 A 选择第一个数据源，填写对应的查询语句。
5. 点击 Add query 添加查询 B，为它选择第二个数据源并填写查询。
6. 检查两个查询各自的返回结果，再选择适合的可视化方式并保存面板。

两条查询仍然使用各自数据源的查询语言。Mixed 负责让它们出现在同一面板中，不会自动把两个后端变成一个数据库。

## 表格中为什么会出现多个结果

多个查询返回的数据可以是独立的数据帧。只切换到 Mixed，不会自动按业务字段把它们拼成一张表。

如果希望按共同字段关联两份结果，可以在 Transformations 中添加 `Join by field`，再选择关联字段。这个字段需要在各份结果中具有可匹配的含义和值。INNER 只保留成功匹配的行，OUTER 可以保留未匹配的行；普通表格数据与时间序列还需要选择相应的模式。

Grafana 10.1 已加入 `OUTER (TABULAR)` 选项，适用于表格数据的外连接。实际配置时，先检查各查询的原始结果和字段类型，再检查转换后的表格，避免把关联字段或时间范围不一致误判成数据源故障。

数据量较大时，应先在数据源端限制查询范围，再考虑面板中的转换。


## Grafana 表格大文本换行（text wrap）

相关版本讨论见 [Grafana 社区的表格换行主题](https://community.grafana.com/t/wrapping-text-in-latest-grafana-10-table/110982)。

使用 Overrides 中的 Cell value inspect 功能，鼠标悬浮在大块文本上时，右侧会显示一个查看图标，点击后可以预览完整内容。
这个功能用于查看单元格的完整内容，与直接在表格中自动换行是两项不同的功能。具体换行选项需要按所用 Grafana 版本确认。




配置完查询后，如果还需要分享面板，应先确定接收方是否拥有登录权限，以及是否需要实时数据。

## Grafana 公开面板

### 1. 匿名访问（Anonymous Access）
Grafana 支持匿名访问，可以允许所有用户无需登录即可访问特定看板。这种方式通常在内网或者对安全要求不高的场景使用。

**设置方法**
1. 编辑 `grafana.ini` 配置文件
2. 找到并修改对应配置。
   ```ini
   [auth.anonymous]
   enabled = true
   org_role = Viewer
   ```
3. 重启 Grafana 服务

启用后，匿名访问会使用相应组织的 Viewer 角色及其权限。它可能开放超出单个面板范围的内容，不能把这段配置当成仅公开一个面板的开关。

### 2. 面板快照（Dashboard/Panel Snapshot）
将单个面板或整个 dashboard 制作成 **快照（Snapshot）**，会生成一个全新的访问链接，数据会“静态快照”在此链接上。

- 在仪表盘上点“Share”→“Snapshot”→“Publish Snapshot”
- 复制产生的公开 URL，任何人都可以访问
- 公开快照的数据为你导出那一刻的快照，**不会自动更新**

### 3. 共享链接（Share Link，需要登录权限）
通过“Share”按钮复制 dashboard 或面板的链接，但受权限控制，外部用户无法直接访问。

### 4. 反向代理和访问控制
你也可以通过 Nginx、Apache 等设置反向代理，为部分面板设置开放的 URL，但**本质上还是依赖 Grafana 后端权限配置**。

### 5. Embedding（嵌入外部页面）
- 用 IFrame 等方式将面板嵌入自己的网页，前提 Grafana 设置成匿名可访问。
- 参考 Share 面板→Embed

---

## 注意事项

- **安全性**。公开访问可能暴露敏感数据，应先检查指标和字段。
- **使用场景**。演示需要公开访问时，应使用已脱敏的内容。
- **数据刷新**。Panel Snapshot 保留当时的数据，不会实时刷新。

---

### 总结

- 要让“Grafana 公开面板”，推荐使用匿名访问或快照分享的方法。
- 强烈建议根据业务需求权衡数据安全和易用性。

直接分享链接仍受访问权限约束。快照保留当时可见的数据，即使系统移除了查询等信息，也需要检查指标、序列名称和业务数据是否适合公开。

## Grafana 表格数据导出

在面板的 Inspect 中导出，支持多数据源的数据组合导出。

导出前检查是否启用了 Apply panel transformations，确认导出的是原始查询结果还是经过面板转换后的结果。

## 参考资料

- [Grafana 数据源与 Mixed 说明](https://grafana.com/docs/grafana/latest/datasources/)
- [多个数据源的官方示例](https://grafana.com/blog/how-to-work-with-multiple-data-sources-in-grafana-dashboards-best-practices-to-get-started/)
- [Join by field 的操作与模式](https://grafana.com/docs/learning-paths/data-transformation/join-by-field/)
- [Grafana 10.1 表格外连接更新](https://grafana.com/docs/grafana/latest/whatsnew/whats-new-in-v10/whats-new-in-v10-1/)
- [表格单元格查看功能](https://grafana.com/docs/grafana/latest/visualizations/panels-visualizations/visualizations/table/)
- [面板与仪表盘分享说明](https://grafana.com/docs/grafana/latest/visualizations/dashboards/share-dashboards-panels/)
