最近，公司迁移Azure API Management到stv2，但仍然打算使用之前的Azure Application Gateway，所以借此机会学习一下这个服务，配置、使用场景以及记录一下由此的引申思考。

### 首先啥是Application Gateway
在[官方文档](https://learn.microsoft.com/en-us/azure/application-gateway/overview)已经有很详尽的解释和介绍，大体上来说是个负载均衡的角色， 但是和传统意义上的负载均衡不同的是它是在应用层发挥作用的，可以按照规则对不同的URI地址进行路由。

### 咋配置Application Gateway
由于这此的任务只是为新的backend（stv2 APIM）配置AppGW，许多原有的配置是不需要改动的，比如：

- Frondend IP configuration：已经配置了public和 private IPs，如果没有特别要求，后续新增配置可以复用现成的。

Azure Portal端的配置包括：

- Backend pools
- Backend settings
- Listeners （Listener & Listener TLS certificates）
- Rules
- Rewrites
- Health probes

其中很多配置之间彼此存在依赖或关联关系，例如：Rules的配置需要Backend pool，Listener和Backend setting，而Backend setting配置时又需要Health probe的配置，等等。所以在分析依赖关系后按照如下顺序配置可以在一定程度上避免反复配置, 整体关系如图所示：

<img src="https://github.com/user-attachments/assets/f79b751d-7684-4353-8c45-606dfccb7a2c" height="600">

1. Backend pool:
    A backend pool is a collection of resources to which your application gateway can send traffic. A backend pool can contain virtual machines, virtual machines scale sets, IP addresses, domain names, or an App Service. 这里配置的是APIM的custom domain。

    ![image](https://github.com/user-attachments/assets/aad451e3-910e-47a8-8e3f-cbeb8349710f)

2. Health probes:
   Like all load balancers, there are health probes configured and monitoring backends' health status, and route traffic only to those that are healthy. Here need to create health probes, and save without verifying, as no backend settings being configured yet.
   On the 'Path', service like APIM has default health check endpoint as '/status-0123456789abcdef', other services like [App Service](https://learn.microsoft.com/en-us/azure/app-service/monitor-instances-health-check?tabs=python) or VMs, they can have custom health probe configured.
 
   <img src="https://github.com/user-attachments/assets/1acf904c-068e-4bf5-b8ae-eefb27acd0d0" height="600">

3. Backend settings:
    Configures backend protocol (http/https), port, cookie, connection draining, timeout, and probe association. Once here is linked to a probe created in above, the probe page will also show the link to this backend settings.

    <img src="https://github.com/user-attachments/assets/b2768e1e-34d1-4799-9c4b-940bb54cad61" height="600">

4. Listener TLS certificates
    This is at the second tab in "Listener" setting, a TLS certificate can support many listeners' configuration. The certificate can either be uploaded or stores in a Key Vault that Application Gateway's identity have access to, the company is using a custom managed identity. The certificate's alternative names should cover all the domain names at the backend (added in backend pool) as well as all the domain names used in Listener (calling it frontend).

    <img src="https://github.com/user-attachments/assets/624f7e55-57a5-4e8f-b28e-d50674b315da" height="400">

5. Listener
    Types:
    * Basic: 接受所有的请求并且转发给backend pools。
    * Multi-site: 按照host header或host name转发给不同的backend pool，注意这里的host是监听的地址，监听的host name是`api-uat.dataops.us.kg`和`api-uat.dataops.org`，那么发送到监听任一地址的请求会被识别并且按照路由规则（在下一步配置）转发到后端。
    
    Protocal:
    * HTTP: 默认端口80，可配置
    * HTTPS: 默认端口443，可配置
    
    Cert：选择在上一步配置的TLS Certificate
6. Rules
    这里的rule就是路由规则，就是监听器收到请求了，咱得定义按照什么规则转发给后端，粗一点说就是哪个萝卜哪个坑。后端这里还包括backend pool（step 1）和backend setting（step 3）；其实这里还有别的玩法，比如可以重定向，由一个监听器转发给另一个监听器或者外部网站，还比如可以按照URL的地址`/`转发，就是`api-uat.dataops.us.kg/log`中的`/log`部分，这就是Application Gateway被认为是在OSI第7层上的负载均衡的原因。关于OSI Layer 7，参见我的另一篇博文“[OSI层级是啥，咋弄，为啥](https://github.com/aiden-liu/aiden-liu.github.io/issues/7)”。
7. Rewrite
    这也是个十分灵活的配置，我认为Rewrite连同Rules构成了整个Application Gateway的灵魂所在。这里rewrite是在rule基础之上定义的，可以看成进一步的routing，但同时也能起到过滤敏感信息等作用。具体咋个意思呢，就是重写请求和响应，包括地址，header，查询参数等。比如针对preflight，可以在这里重写response headers`Access-Control-Allow-Origin`等。

另外: 确保所有的 private DNS names都在Azure Private DNS Zones中添加了，而且每个DNS Zone添加了对应的 A Records 或CNAMEs，否则在测试health probe过程中会报错DNS不识别。
