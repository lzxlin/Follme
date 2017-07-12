# Follme

数据库课程设计--一个小型的个人微博吧。

初次涉略前端，django等知识。

特点：

（1）“follow me”简称


（2）添加好友的方式不需要经过对方的同意，可以通过RP值和拦截器来限制恶意操作。就是说，不管你愿不愿意，我都可以加你为好友，当然，对方也可以取消你，并且会付出相应的代价。这有利于减少成为好友之间的操作。


（3）RP值计算（初始RP值为60，当RP<0被封号）

功能需求：
消息发布和删除，评论发布和删除以及回复，支持多级评论

消息点赞和踩，评论点赞

消息通知（包括点赞，踩以及评论）

好友添加，删除，推荐，查询

利用缓存实现在线人数统计，消息浏览数统计

RP值计算，记录RP的操作过程

个人信息的编辑

暂不支持转发和@的功能，话题讨论，以及表情的发送


使用到的技术：

（1）中间件技术，实现在线人数统计。这里采用IP地址作为在线认证。

（2）信号机制signals，实现消息的通知。

（3）本地缓存，减少对数据库的操作。实现了在线人数统计，消息统计等。

（4）自定义过滤器，实现对消息空格的处理。

（5）递归寻找子评论，实现多级评论。

（6）采用django内置的服务器，由于性能原因，一般只适用开发人员测试，不适合用于部署和发布。


数据库：PostgresSQL

