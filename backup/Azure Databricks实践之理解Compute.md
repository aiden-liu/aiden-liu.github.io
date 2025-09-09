### 为什么要深入理解Azure Databricks的Compute

起因是发现pyspark代码在有的all purpose compute上就能跑成功，有的就报一些莫名其妙的错误，花了很多时间troubleshoot，感觉就像跳进兔子洞，却没有什么实质进展。所以与其被动的troubleshoot，不如趁此机会仔细了解下Azure Databricks的compute是怎么回事。

这种情况相信很多做数据工程的同学都遇到过：同样的代码，在不同的计算集群上表现不一致。有时候是库版本冲突，有时候是配置问题，有时候是资源不够，但往往找不到根本原因。

### 啥是Azure Databricks Compute

Azure Databricks Compute本质上就是一个托管的Apache Spark集群。但它不是简单的Spark集群，而是经过优化的、与Azure深度集成的计算环境。

主要有以下几种类型：

**All-Purpose Clusters (通用集群)**
- 交互式开发用的集群
- 可以运行notebooks、ad-hoc查询
- 支持多用户同时使用
- 可以手动启动和停止
- 适合数据探索和开发调试

**Job Clusters (作业集群)**
- 专门运行scheduled jobs的集群
- 作业运行完自动终止，节省成本
- 每个job可以有独立的配置
- 适合生产环境的数据pipeline

**SQL Warehouses (SQL仓库)**
- 专门用于SQL查询和BI工具
- 基于Photon引擎，查询性能更好
- 支持serverless模式
- 适合数据分析师使用

### Databricks Runtime是个啥

这里必须要理解一个核心概念：Databricks Runtime (DBR)。这是Databricks在开源Spark基础上的优化版本，包含了：

- 优化的Spark引擎
- 预装的常用库（pandas, scikit-learn, tensorflow等）
- Delta Lake支持
- MLflow集成
- 安全和性能优化

不同的Runtime版本包含不同的Spark版本和Python库版本，这就是为什么同样的代码在不同集群上表现不一致的关键原因。

**常见的Runtime类型：**
- Standard Runtime：标准版，包含基础的数据工程库
- ML Runtime：机器学习版，预装了大量ML库
- Photon Runtime：包含Photon引擎，查询性能更好
- Light Runtime：轻量版，启动更快但功能较少

### 为啥同样的代码在不同Compute上表现不一致

这个问题的答案主要有以下几个方面：

**1. Runtime版本不同**
不同的DBR版本包含不同的：
- Spark版本（2.4.x vs 3.x差别很大）
- Python版本（3.7 vs 3.8 vs 3.9）
- 预装库的版本（pandas 1.x vs 2.x）
- JVM版本和配置

**2. 集群配置不同**
- Worker节点数量和规格
- Driver节点规格
- 内存配置
- Auto-scaling设置

**3. 库依赖冲突**
- 有些集群安装了自定义库
- 不同Runtime预装库版本冲突
- pip install的库版本不一致

**4. 环境变量和配置**
- Spark配置参数
- 环境变量设置
- 安全配置

### 怎么排查Compute相关的问题

**步骤1：确认Runtime版本**
```python
# 在notebook中运行，查看当前环境信息
print(f"Spark version: {spark.version}")
print(f"Python version: {spark.sparkContext.pythonVer}")

# 查看DBR版本
dbutils.notebook.run("/databricks/python/lib/python3.8/site-packages/databricks/version.py", 0)
```

**步骤2：检查预装库版本**
```python
import pandas as pd
import numpy as np
import pyspark

print(f"pandas: {pd.__version__}")
print(f"numpy: {np.__version__}")
print(f"pyspark: {pyspark.__version__}")
```

**步骤3：查看集群配置**
在集群详情页面检查：
- Runtime版本
- 节点类型和数量
- Spark配置
- 环境变量
- 安装的库

**步骤4：统一环境**
- 使用相同的Runtime版本
- 在init script中统一安装依赖库
- 使用requirements.txt固定库版本
- 配置相同的Spark参数

### 最佳实践：如何选择和配置Compute

**开发阶段：**
- 使用All-Purpose Cluster
- 选择较新的ML Runtime（预装库多）
- 配置auto-termination，避免忘记关闭
- 使用较小的集群规模（Single Node或2-3个worker）

**生产阶段：**
- 使用Job Cluster
- 选择稳定的Runtime版本
- 根据数据量配置合适的集群规模
- 使用init script统一环境
- 配置监控和alerting

**性能优化：**
- 对于SQL heavy的workload，考虑使用Photon Runtime
- 合理配置executor memory和cores
- 启用adaptive query execution
- 使用Delta Lake进行存储优化

### 常见的Compute问题和解决方案

**问题1：OutOfMemoryError**
```
# 解决方案：增加executor memory或减少partition大小
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
spark.conf.set("spark.sql.adaptive.advisoryPartitionSizeInBytes", "128MB")
```

**问题2：库版本冲突**
```bash
# 使用init script统一安装特定版本的库
#!/bin/bash
pip uninstall -y pandas
pip install pandas==1.5.3
```

**问题3：Job运行缓慢**
- 检查数据倾斜问题
- 优化join策略
- 使用broadcast join
- 调整并行度

**问题4：集群启动失败**
- 检查网络配置
- 验证权限设置
- 查看driver logs
- 确认配额限制

### 总结

理解Azure Databricks Compute的关键在于：
1. **Runtime选择**：根据使用场景选择合适的Runtime版本
2. **环境一致性**：开发和生产环境保持一致
3. **配置标准化**：使用init script和cluster policy标准化配置
4. **监控调优**：持续监控性能并根据需要调优

通过深入理解这些概念，就能避免很多莫名其妙的问题，让数据工程工作变得更加可预测和可靠。

记住：**好的工程师不是不遇到问题，而是能够系统性地理解和解决问题。**