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

以上要求的1至5点，除了新建cert之外，都是由landingzone实现的，不在这里展开，详细可参见我的另一篇帖子[Terraform实战（进阶篇）](https://blog.dataops.us.kg/post/Terraform-shi-zhan-%EF%BC%88-jin-jie-pian-%EF%BC%89.html)。这里着重说一下6到9的实现。

关于tier的说明可以参看[官方文档](https://learn.microsoft.com/en-us/azure/api-management/api-management-capacity?tabs=v2-tiers)，注意的几点就是：
1. 多点部署需要Premium
2. 不同tier的备份和还原是不互通的，Developer的备份只能还原到Developer的实例上。关于备份和还原，可以看我的另一篇帖子[API Management stv2（迁移篇）](https://blog.dataops.us.kg/post/API%20Management%20stv2%EF%BC%88-qian-yi-pian-%EF%BC%89.html)

系统管理身份（System Managed Identity）其生命周期和对应的资源绑定，另一种管理身份是客户管理身份（Custom Managed Identity），其生命周期独立于资源，可以同时被多个资源使用，通常用在某一资源不支持SMI的情况。这里遇到第一个坑：
> Official note: 
It's possible to define Custom Domains both within [the azurerm_api_management resource](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/api_management) via the hostname_configuration block and by using [the azurerm_api_management_custom_domain resource](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/api_management_custom_domain). However it's not possible to use both methods to manage Custom Domains within an API Management Service, since there'll be conflicts.

这里没有明确说明的是：在同一个resource block创建custom domain只能使用CMI，如果不想用CMI，那么就得分开创建。因为在同一个资源中，部署成功的前提是能用某种身份获取在key vault中的cert以关联custom domain，假使计划用SMI，在创建APIM时SMI还没有存在，还不能用来访问key vault，因此没法获取cert，因此资源整体部署不成功。形成了死锁，所以要分成两个block部署。

第6点中的subnet不能delegate是硬性要求，这点[官方文档](https://learn.microsoft.com/en-us/azure/api-management/api-management-using-with-internal-vnet?tabs=stv2#prerequisites)中也有提及：
> A virtual network and subnet in the same region and subscription as your API Management instance.
The subnet used to connect to the API Management instance may contain other Azure resource types.
The subnet shouldn't have any delegations enabled. The Delegate subnet to a service setting for the subnet should be set to None.

另外，subnet的service endpoints需要至少包括：[ "Microsoft.Storage", "Microsoft.KeyVault", "Microsoft.Eventhub", "Microsoft.Sql" ]，详见[官方文档](https://learn.microsoft.com/en-us/azure/api-management/api-management-using-with-internal-vnet?tabs=stv2#force-tunnel-traffic-to-on-premises-firewall-using-expressroute-or-network-virtual-appliance)。 

第8点中配置diagnostic setting到log analytics workspace比较直接，关于Log Analytics Workspace的部署参见我的另一篇文章[Log Analytics Workspace（部署篇）](https://blog.dataops.us.kg/post/Log%20Analytics%20Workspace%EF%BC%88-bu-shu-pian-%EF%BC%89.html)，其中有专门的讲解network isolation的实现和注意事项。

第9点要求配置APIM policy，这里不得不提到APIM中API的四层policy，分别是：
1. API Management全局policy，影响所有部署在该实例下的API；
2. APIM产品policy，影响所有部署在该产品下的API，一个产品可以包含0到多个API；
3. API policy，影响该API下所有的operation；
4. API operation policy，影响某一API里某一个operation，属于最底层的policy；
这么多层policy怎么减少代码冗余，APIM中可以定义policy块，在不同层可重复引用。

第10点关于代码仓库管理，编码规范，文档和测试等，可以参考我另一篇文章[Terraform实战（入门篇）](https://blog.dataops.us.kg/post/Terraform-shi-zhan-%EF%BC%88-jin-jie-pian-%EF%BC%89.html)