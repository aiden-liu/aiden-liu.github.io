最近，公司迁移Azure API Management到stv2，但仍然打算使用之前的Azure Application Gateway，所以借此机会学习一下这个服务，配置、使用场景以及其他的引申思考。

### 什么是Application Gateway
在[官方文档](https://learn.microsoft.com/en-us/azure/application-gateway/overview)已经有很详尽的解释和介绍，大体上来说是个负载均衡的角色， 但是和传统意义上的负载均衡不同的是它是在应用层发挥作用的，可以按照规则对不同的URI地址进行路由。

### 怎么配置Application Gateway
由于这此的任务只是为新的backend（stv2 APIM）配置AppGW，许多原有的配置是不需要改动的，比如：

- Frondend IP configuration：已经配置了public和 private IPs，如果没有特别要求，后续新增配置可以复用现成的。

Azure Portal端的配置包括：

- Backend pools
- Backend settings
- Listeners （Listener & Listener TLS certificates）
- Rules
- Rewrites
- Health probes

其中很多配置之间彼此存在依赖或关联关系，例如：Rules的配置需要Backend pool，Listener和Backend setting，而Backend setting配置时又需要Health probe的配置，等等。所以在分析依赖关系后按照如下顺序配置可以在一定程度上避免反复配置：

1. Backend pool:
    A backend pool is a collection of resources to which your application gateway can send traffic. A backend pool can contain virtual machines, virtual machines scale sets, IP addresses, domain names, or an App Service. 这里配置的是APIM的custom domain。
![image](https://github.com/user-attachments/assets/aad451e3-910e-47a8-8e3f-cbeb8349710f)

1. Health probes:
   Like all load balancers, there are health probes configured and monitoring backends' health status, and route traffic only to those that are healthy. Here need to create health probes, and save without verifying, as no backend settings being configured yet.
   On the 'Path', service like APIM has default health check endpoint as '/status-0123456789abcdef', other services like [App Service](https://learn.microsoft.com/en-us/azure/app-service/monitor-instances-health-check?tabs=python) or VMs, they can have custom health probe configured. <img src="https://github.com/user-attachments/assets/1acf904c-068e-4bf5-b8ae-eefb27acd0d0" height="600">

1. Backend settings:
    
   
1. Listener TLS certificates
1. Listener
1. Rules
1. Rewrite

