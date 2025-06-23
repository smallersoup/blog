---
keywords:
- Grafana
title: "Grafana 一个面板配置多数据源"
date: 2025-06-23T05:15:34Z
description: Grafana 一个面板配置多数据源。
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
img: https://images.icloudnative.io/uPic/202109151325055.png
---

参考：
https://grafana.com/blog/2024/11/07/how-to-work-with-multiple-data-sources-in-grafana-dashboards-best-practices-to-get-started/

安装 10.2.2 版本的 Grafana （grafana:10.2.2镜像）是支持混合数据源的。


## Grafana 表格大文本换行（text wrap）

参考：https://community.grafana.com/t/wrapping-text-in-latest-grafana-10-table/110982

使用 Overrides 中的 Cell value inspect 功能，鼠标悬浮在大块文本上时，右侧会显示一个眼睛👁的图标，点击会会弹出一个对话框来预览大段文本。
Cell value inspect
Enable cell value inspection in a modal window




你提到的“**Grafana 公开面板**”，一般指的是将 Grafana 的某个 dashboard（仪表盘）或 panel（单独面板）通过互联网公开给任何人访问，而无需登录权限。

## Grafana 公开面板

### 1. 匿名访问（Anonymous Access）
Grafana 支持匿名访问，可以允许所有用户无需登录即可访问特定看板。这种方式通常在内网或者对安全要求不高的场景使用。

**设置方法：**
1. 编辑 `grafana.ini` 配置文件
2. 找到并修改如下内容：
   ```ini
   [auth.anonymous]
   enabled = true
   org_role = Viewer
   ```
3. 重启 Grafana 服务

这样所有人打开 Grafana 地址都可以以 Viewer（浏览者）权限访问所有 dashboard。

### 2. 面板快照（Dashboard/Panel Snapshot）
将单个面板或整个 dashboard 制作成 **快照（Snapshot）**，会生成一个全新的访问链接，数据会“静态快照”在此链接上。

- 在仪表盘上点“Share”→“Snapshot”→“Publish Snapshot”
- 复制产生的公开 URL，任何人都可以访问
- 注意：公开快照的数据为你导出那一刻的快照，**不会自动更新**

### 3. 共享链接（Share Link）——（登录情况下使用）
通过“Share”按钮复制 dashboard 或面板的链接，但受权限控制，外部用户无法直接访问。

### 4. 反向代理和访问控制
你也可以通过 Nginx、Apache 等设置反向代理，为部分面板设置开放的 URL，但**本质上还是依赖 Grafana 后端权限配置**。

### 5. Embedding（嵌入外部页面）
- 用 IFrame 等方式将面板嵌入自己的网页，前提 Grafana 设置成匿名可访问。
- 参考 Share 面板→Embed

---

## 注意事项

- **安全性**：彻底的“公开”意味着所有数据都对外暴露，慎重对待敏感或个人数据。
- **使用场景**：建议临时展示、演示等非重要场景使用公开面板。
- **数据刷新**：Panel Snapshot 是静态的，不会实时刷新。

---

### 总结

- 要让“Grafana 公开面板”，推荐使用匿名访问或快照分享的方法。
- 强烈建议根据业务需求权衡数据安全和易用性。

如需具体配置操作指导，请说明你用的是哪种 Grafana 部署方式（Docker、本地、云等）和版本。

## Grafana 表格数据导出

在面板的 Inspect 中导出，支持多数据源的数据组合导出。

Apply panel transformations
Table data is displayed with transformations defined in the panel Transform tab.