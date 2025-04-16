￼
# 🎮 meanig v1.0.0  
  


### 一、图片工具集（关键词触发）  

| 触发关键词                | 功能描述                     | 图片类型               |  
|---------------------------|------------------------------|------------------------|  
| 蔡徐坤、来点坤图（无法使用）          | 获取蔡徐坤相关随机图片         | 随机明星图片           |  
| 丁真、来点丁真图 （无法使用）         | 获取丁真相关随机图片           | 随机人物摄影           |  
| 原神黄历、来点骚的        | 获取原神主题黄历图文           | 二次元图文结合         |  
| 热榜                      | 获取60秒热点资讯图片           | 新闻资讯图片           |  
| 小动物                    | 获取动漫风格动物插画           | 二次元风格动物图片     |  
| 三坑少女                  | 获取三坑服饰风格美女图片       | 时尚穿搭摄影           |  
| 看看妞、看看腿            | 获取人物美拍/腿部特写图片       | 人物摄影图片           |  
| 猫猫                      | 获取萌宠猫咪主题图片           | 治愈系萌宠图片         |  
| 风景、景色                | 获取二次元风格风景CG图片       | 二次元场景插画         |  
| 随便来点                  | 随机获取各类风格图片           | 综合类型图片           |  
| 龙图                      | 获取东方幻想风格龙主题图片     | 奇幻风格插画           |  
| cosplay、来点cos          | 获取角色扮演Cosplay图片         | 三次元Cosplay摄影      |  
| 全国阵雨（存在问题无法使用）| 获取天气主题阵雨场景图片       | 天气相关插画           | 
| 来点二次元                | 获取动漫风格美女插画           | 二次元美少女插画       |  
| 海贼王、蜡笔小新          | 获取对应动漫角色官方/同人图     | 动漫IP角色图片         |  
| doro结局                  | 获取Doro游戏剧情结局图片       | 游戏CG剧情图片         |  
| 早安、晚安                | 获取早晚问候主题温馨图片       | 治愈系问候插画         |  
| 历史上的今天              | 获取历史事件回顾资讯图片       | 历史资讯图文           |  
| 腹肌                      | 获取健身腹肌主题摄影图片       | 运动健身图片           |  
| 来点原神                  | 获取原神角色/场景官方插画       | 游戏IP插画             |  
| 弔图 （存在问题）          | 获取网络热门搞笑趣味图片       | 梗图/搞笑图片          | 

### 二、趣味互动 & 实用工具  

| 功能分类       | 指令/关键词         | 格式说明                          | 核心特性                                                                 |  
|----------------|---------------------|-----------------------------------|--------------------------------------------------------------------------|  
| 趣味互动       | 左右脑互搏          | `/左右脑互搏 [轮数]`（默认3轮）    | 大语言模型生成对战台词，模拟辩论赛场景，随机结局附带图片，支持1-10轮自定义。 |  
| 文本工具       | 点阵字生成          | `点阵字 [内容] [填充符]`           | 将文字转换为点阵字符图案 |  
| 信息查询       | 求签                | `求签`                            | 随机生成签文，自动优化格式（换行/标点），支持多行展示，内容包含运势解析。    |  
| 资讯获取       | 每日日报            | `每日日报`                        | 获取图文日报（热点新闻/生活建议），附带音乐推荐链接，支持多平台消息格式。    |

## 🛠 技术优势 & 适配性  

| 特性                | 说明                                                                 |  
|---------------------|----------------------------------------------------------------------|  
| **异步处理**        | 基于 `asyncio` 实现高并发消息处理，拒绝阻塞，支持海量消息流稳定运行  |  
| **热重载支持**      | 修改代码后无需重启，管理面板一键重载插件，开发调试效率拉满          |  
| **统一配置管理**    | 支持网页控制台配置插件参数，自动生成帮助文档与权限控制体系          |  
| **LLM深度集成**     | 调用大语言模型生成动态内容，支持温度/令牌数等参数自定义             |  

### 🚀 快速开始  
- **指令调用**：  
  ```  
  /左右脑互搏 5  # 5轮对战  
  点阵字 爱你 爱  # 生成含✨的点阵字  
  ```  
- **关键词触发**：直接发送 `蔡徐坤` `来点丁真图` 等关键词，自动返回对应图片  


## 📖 文档 & 社区  

- **详细文档**：[AstrBot插件开发指南](https://github.com/ttq7/meanig)
- **控制台**：网页端实时监控插件状态、日志检索、配置热更新（需开启AstrBot管理面板）  


## 🙏 致谢 & 协议  

- 本插件基于 **MIT 许可证** 开源，允许自由修改与分发 
- 感谢 [AstrBot社区](https://github.com/AstrBotDevs) 提供的开发支持与测试反馈  
- 图片API来源：小BAPI、星之鸽API、317AK等公开接口，感谢数据提供者  
