开源日记 开源日记

在小说阅读器读本章

去阅读

数据库也能像 Git 一样进行 fork、branch 和 merge 吗？

答案是：可以。

最近在 GitHub 上刷到一个叫 Dolt 的项目。

它做的事情就是让你用 Git 的方式来管理数据库。

目前 GitHub 上有 23K Star。

它不是在数据库外面套一层版本控制，而是从存储层原生支持分支、提交、合并这些操作。

修改一行数据可以提交版本，创建分支做测试不影响主库，确认没问题后再合并回去。

可以说，Dolt 是目前最接近“Git for Database”理念的 SQL 数据库之一。

![](https://mmbiz.qpic.cn/mmbiz_png/VDCUoW3UiblIFiaTGJicVrBe0loeSLHbLPeToo8wOFibp7f2lXpnTH9icF5gkL4jgX6tdyfrMWlpeSxzXnSy3X7WtmYWj789pdoGjNIUfic1Qa0wg/640?wx_fmt=png&from=appmsg)

## 它把数据库版本控制的主要功能都给你了

**01 行级历史追踪。**

Dolt 会为每个表自动生成一个叫做 `dolt_history_tablename` 的历史视图。

要查询某一个数据单元格是谁在什么时间修改的，直接查看该视图即可。

例如员工表中 ID=0 这条记录，从最早版本到当前版本的所有变更内容，都能直接查看。

```
SELECT * FROM dolt_history_employees WHERE id = 0;
```
![](https://mmbiz.qpic.cn/sz_mmbiz_png/VDCUoW3UiblKoGJ3omrg2dUxGTxMz2iaTH973rBPLic567Ysxl4micGOicRE610O6sDfKs6Rw6aQ0lVHuNEX2ROD3sKYwJkzlOYz6wdMY2x1afns/640?wx_fmt=png&from=appmsg)

不需另外设置，默认就有。

**02 分支工作流。**

你可以创建一个数据分支，在上面做实验、改数据、跑测试，完全不影响主数据。

分支可以持续数周甚至数月，不像数据库事务只能撑几秒。

等到实验结束之后，确定没有问题了才把它们合并到主分支上。如果有冲突的地方，Dolt 会帮你检测并提示。

对于数据分析和数据科学团队来说这个功能非常管用。

以前要在生产数据上做实验，一般是复制一份数据出来。现在简单了，直接开个分支就行。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/VDCUoW3UiblLVHPQ49pljEGGTR30vicrDnBhxSjfE92uYCeT5kSpAEvg0NuYibHibMrlY2nXW8gMRe2qQ9w7ltT6UhqrtxwmzeM8XElen4nDgmE/640?wx_fmt=png&from=appmsg)

**03 AI Agent 的安全操作。**

Dolt 还发布了 MCP Server，使 AI Agent 也能够使用标准协议来操作数据库。

AI Agent 可以在独立分支上干活。改了一堆数据，你先检查再合并。

如果修改错了就直接放弃该分支就可以了，主数据不会受到影响。

这样比直接把 AI 放到生产库里面去跑 SQL 要安全得多。

![](https://mmbiz.qpic.cn/mmbiz_jpg/VDCUoW3UiblIZf1VibmA9UG5YhCLGL3SsfhDNEX3Gv9pQDthld6bVmiayyGFm5PiahVd6kcb4ZRwdvx8UmdCpfrlNbRAB2Th5CcIqh9oBmGUeV4/640?wx_fmt=other&from=appmsg)

**04 Dolt Workbench 可视化界面。**

Dolt 还有一个开源的图形化工作台可以用来操作 MySQL 和 PostgreSQL。

切换分支、查看提交日志、对比分支差异，这些操作都有可视化界面。

不需记命令，点击按钮就可以实现创建、合并和回退。

![](https://mmbiz.qpic.cn/mmbiz_jpg/VDCUoW3UiblI0RDoGgKYAh24D8MV1xySRg1A9RHImMBvYxGOhAE58LhSJIUcj39GjJUxjZvyrgSqzJtUn3nVlBlCMkyRs1wNzaFb2dia1XBcM/640?wx_fmt=other&from=appmsg)

对不熟悉 Git 的数据分析师来说，这个带界面的操作就友好很多。

**05 MySQL 协议兼容。**

Dolt 兼容 MySQL 5.7 协议，所以绝大多数 MySQL 客户端都能直接连接使用。

像 Navicat、DBeaver、DataGrip 这些常见工具基本不用额外配置，直接连就行。默认端口是 3306，用户名 root，密码留空。

进去之后就可以正常的建表、插数据、做 commit 了。

## 和传统备份方案有什么区别

大部分团队的“数据库版本控制”就是指定期做备份再加上 binlog ssss回放。有如下两个问题：

第一就是颗粒度太大。备份可以恢复到某一个时间点上，但是不能看到是谁修改了哪一行。

第二个就是合作的成本比较高。两个开发人员同时修改数据的时候，要不互相锁定，要不通过沟通来防止冲突。

Dolt 的思路完全不同：备份变"提交"，恢复变"回滚"，数据实验变"分支"。

不需要等到修改之后再看日志了，在修改之前就可以看到差别。

![](https://mmbiz.qpic.cn/mmbiz_png/VDCUoW3UiblKtWG8pteptsbNAsc9ibO4lMiaickhlSdJM4os1yCBvziaibUatSlTgYq7UasWPsMQa4kUxEon1z2Vxib9rYBlicuCjmhoBmdKUczOEvk/640?wx_fmt=png&from=appmsg)

根据官方 Sysbench 测试结果，在读写方面，Dolt 已经接近于MySQL了。在TPC-C测试中，TPS大约为 MySQL的54%，对于大部分的应用来说是够用的。

## 看到这，有些人可能想试试

最简单就是从Github下载安装包。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/VDCUoW3UiblLtFLYlNN8qvw7YuCKnmDncblTia01ta8E3wY0RHERI9WBrDraQpuZFLxX1EvG01X1zLMMSibRTCXojj87RNTc0QdZgCxWrzW9yk/640?wx_fmt=png&from=appmsg)

Mac, Windows, Linux 都有。

安装好之后设置用户名、邮箱等信息（与 Git 类似），继续

```
dolt init
dolt sql server
mysql--host=127.0.0.1--port=3306-uroot
```
![](https://mmbiz.qpic.cn/sz_mmbiz_png/VDCUoW3UiblLER4IjyYK6mhcu2zHFutoRcwT7Rpyn3qGGvB0Vbu2Jb3ICHngbmEicspqYDyt7uUSoRibMic35oEoskgnPufibGVrfzqouA41TADk/640?wx_fmt=png&from=appmsg)

然后打开 TablePlus 或者 DBeaver 直接连接，创建表、插入数据、执行 commit 等操作都十分自然。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/VDCUoW3UiblIjLl3CTicBhtuqx4Pe7rJyS6j4TqPicicDb86xFfzVHoUw4S3VEhZx5Yx4RRuLp8u81kriaqllLuprOOU1AkMXU1dc18ibibTibp3dJY/640?wx_fmt=png&from=appmsg)

建议先用小数据量测试版本控制功能，体验 `dolt branch` 、 `dolt merge` 、 `dolt log` 。

我用下来。

整个过程跟Git 差不多，只不过操作的对象是数据而非常见的文件。

## 但是问题也要给大家提一下

功能看起来很好，但是实际使用中会存在一些限制，提前了解一下少走点弯路。

按照社区对它的评价，在处理超过 1G 的数据的时候就会变得比较慢了。

对复杂的查询来说也会比 MySQL 还要慢一点。

另外。Dolt 不能“叠加”到现有的数据库上面去，必须要把数据迁移到这里来才行。

如果业务系统不能修改，那 Dolt 就很难直接接管数据库。

更常见的做法是把数据定期同步到 Dolt，让它负责记录和追踪数据变化。

## 写在最后

过去改错数据，要么靠备份恢复，要么翻审计日志倒查，发现问题时往往已经晚了。

Dolt 将版本控制放在了数据库底层，每一条记录的变化都可以被追踪到。

分支、合并、回滚等Git中的操作，在数据库中也可以直接使用了。

我试了一把，整个过程和 Git 操作一模一样。

感兴趣的朋友可以装上试试。

项目基于 Apache-2.0 协议开放，感兴趣的同学可以去 GitHub 看看源码和文档。

开源地址：https://github.com/dolthub/dolt

既然看到这了，欢迎随手点赞、在看、转发，也可以给我个星标⭐，我们下期见 ！

微信扫一扫  
使用小程序

： ， ， ， ， ， ， ， ， ， ， ， ， 。 视频 小程序 赞 ，轻点两下取消赞 在看 ，轻点两下取消在看 分享 留言 收藏 听过