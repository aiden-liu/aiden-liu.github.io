部署一个新的Azure API Management（APIM）实例是个挺磨人的活儿，主要原因是迭代费劲，不管在网页端（Azure portal）部署还是通过IaC（Infrastructure as Code）部署，单次部署时长通常不少于30分钟，如果反复修改调整，差不多一天出去了。所以本文列出通过IaC常规的部署步骤，以及一些[官网](https://learn.microsoft.com/en-us/azure/api-management/api-management-using-with-internal-vnet?tabs=stv2)没有提及的坑。

这里要交代一下架构，以方便读者理解为什么这么做，并按照自己的情况调整：
0. 以下所有部署均使用Terraform完成，资源命名规则另见文档；
1. 为每个环境新建subscription；
2. 在每个subscription中新建一个virtual network, 且包含默认subnet，其地址空间为/26，包含指定规则的route table；
3. 新建的Vnet peer到已有的Hub Vnet上。
4. 新建key vault，并添加cert， cert名称应涵盖所有的私有域名以及APIM的builtin域名。
5. 新建APIM，tier为Developer， 单点，系统管理身份，配置internal模式，使用步骤2中的vnet，新建subnet，其地址空间为/26，包含指定规则的route table；
6. 为APIM配置私有域名，为每个域名配置A record到对应的Private DNS Zone中，域名所需cert来自步骤4，使用系统管理身份访问。
7. 为APIM配置monitor，使用diagnostic setting，分别发送到指定的log analytics workspace和event hub中。
8. 为APIM配置全局policy，使用指定CORs rule。
9. 其他：包括代码仓库管理，编码规范，文档和测试等。

