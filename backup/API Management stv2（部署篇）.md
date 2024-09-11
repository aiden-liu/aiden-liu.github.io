部署一个新的Azure API Management（APIM）实例是个挺磨人的活儿，主要原因是迭代费劲，不管在网页端（Azure portal）部署还是通过IaC（Infrastructure as Code）部署，单次部署时长通常不少于30分钟，如果反复修改调整，差不多一天出去了。所以本文列出通过IaC常规的部署步骤，以及一些[官网](https://learn.microsoft.com/en-us/azure/api-management/api-management-using-with-internal-vnet?tabs=stv2)没有提及的坑。

这里要交代一下架构，以方便读者理解为什么这么做，并按照自己的情况调整：
1. 以下所有部署均使用Terraform完成，资源命名规则另见文档；
2. 为每个环境新建subscription；
3. 在每个subscription中新建一个virtual network, 且包含默认subnet，其地址空间为/26，包含指定规则的route table；
4. 新建的VNet peer到已有的Hub Vnet上。
5. 新建key vault，并添加cert， cert名称应涵盖所有的私有域名以及APIM的builtin域名。
6. 新建APIM，tier为Developer， 单点，系统管理身份，网络隔离配置internal模式，使用步骤2中的vnet，新建subnet，其地址空间为/26，包含指定规则的route table；
7. 为APIM配置私有域名，为每个域名配置A record到对应的Private DNS Zone中，域名所需cert来自步骤4，使用系统管理身份访问。
8. 为APIM配置monitor，使用diagnostic setting，分别发送到指定的log analytics workspace和event hub中。
9. 为APIM配置全局policy，使用指定CORs rule。
10. 其他：包括代码仓库管理，编码规范，文档和测试等。

以上要求的1至5点，除了新建cert之外，都是由landingzone实现的，不在这里展开，详细可参见我的另一篇帖子[Terraform实战（进阶篇）](https://github.com/aiden-liu/aiden-liu.github.io/issues/13)。这里着重说一下6到9的实现。

关于tier的说明可以参看[官方文档](https://learn.microsoft.com/en-us/azure/api-management/api-management-capacity?tabs=v2-tiers)，注意的几点就是：
1. 多点部署需要Premium
2. 不同tier的备份和还原是不互通的，Developer的备份只能还原到Developer的实例上。关于备份和还原，可以看我的另一篇帖子[API Management stv2（迁移篇）](https://github.com/aiden-liu/aiden-liu.github.io/issues/8)

系统管理身份（System Managed Identity）其生命周期和对应的资源绑定，另一种管理身份是客户管理身份（Custom Managed Identity），其生命周期独立于资源，可以同时被多个资源使用，通常用在某一资源不支持SMI的情况。这里遇到第一个坑：