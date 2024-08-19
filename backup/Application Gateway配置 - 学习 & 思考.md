最近，公司迁移Azure API Management到stv2，但仍然打算使用之前的Azure Application Gateway，所以借此机会学习一下这个服务，配置、使用场景以及其他的引申思考。

### 什么是Application Gateway
在[官方文档](https://learn.microsoft.com/en-us/azure/application-gateway/overview)已经有很详尽的解释和介绍，大体上来说是个负载均衡的角色， 但是和传统意义上的负载均衡不同的是它是在应用层发挥作用的，可以按照规则对不同的URI地址进行路由。