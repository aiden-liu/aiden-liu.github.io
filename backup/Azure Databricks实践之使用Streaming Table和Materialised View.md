### 什么是Streaming Table
Streaming tables原理是常规delta table加上用于streaming或处理增量数据的data pipeline，所构成的一种表。在Table detail中的类型为STREAMING_TABLE。适用情况有：
* 每行数据仅需要处理一次；
* 处理大量的增量数据；

其同时也具备以下特点：
* 无需指定，每行数据都有其对应的时间戳；
* 能处理大批量的数据
* 而且处理的快

可以通过DLT pipeline来定义和更新streaming tables，这样的streaming table是和pipeline一对一绑定的且不能被其他的pipeline更改。或者另一种方式是直接通过SQL定义streaming table，Databricks会自动创建一个DLT pipeline，这个pipeline是默认隐藏的，仅可以通过table lineage进入，不能手动更改，但是可以手动触发运行。

### 怎么用Streaming Table

### 什么是Materialised View

### 怎么用Materialised View

### 为什么用Streaming Tables和Materialised Views