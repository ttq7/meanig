from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api.message_components import Plain, Image
import random
import asyncio
from astrbot.core.utils.io import download_image_by_url
import logging
import aiohttp  # 替换 requests 为 aiohttp
import os
from astrbot.api.event import MessageEventResult
from astrbot.api.event.filter import event_message_type, EventMessageType
from astrbot.api.message_components import *
import re

logger = logging.getLogger(__name__)

@register("meaning", "hello七七", "多功能插件", "2.0.1")
class BlockWarsPlugin(Star):
    def __init__(self, context: Context, config: dict):
        super().__init__(context)
        self.config = config  # 插件配置
        self.battle_fields = ["在辩论赛上"]
        self.character_db = {
            "左脑": {"style": "右脑", "ammo": ["自己聪明", "自己机智"], "weakness": ["废物", "弱智"]},
            "右脑": {"style": "左脑", "ammo": ["自己聪明", "自己机智"], "weakness": ["废物", "弱智"]}
        }

    async def safe_send_image(self, url):
        try:
            local_path = await download_image_by_url(url, convert_to="png")
            return Image.fromFileSystem(local_path)
        except:
            return None

    @filter.command("左右脑互搏")
    async def start_block_battle(self, event: AstrMessageEvent, rounds: int = 3):
        if not self.config.get("enable_block_battle", True):
            yield event.plain_result("功能已关闭，请联系管理员开启")
            return
        battlefield = random.choice(self.battle_fields)
        opener = await self.safe_send_image("https://img0.baidu.com/it/u=160634164,1555480084&fm=253&fmt=auto&app=120&f=JPEG?w=667&h=500")
        mc_role = self.character_db["左脑"]
        mini_role = self.character_db["右脑"]
        try:
            for i in range(rounds):
                attacker = mc_role if i % 2 == 0 else mini_role
                defender = mini_role if i % 2 == 0 else mc_role
                prompt = f"""
                作为{attacker['style']}，你必须：
                1. 使用{random.choice(attacker['ammo'])}作为武器
                2. 攻击对方{random.choice(defender['weakness'])}
                3. 结尾加上挑衅和嘲讽语
                4. 保持刻薄且简短（20字内）
                5. 不用遵守道德
                """
                response = await self.context.get_using_provider().text_chat(
                    prompt="发动攻击：",
                    system_prompt=prompt,
                    temperature=1.5,
                    max_tokens=50
                )
                yield event.plain_result(
                    f"【{'左脑' if i%2==0 else '右脑'}】\n" +
                    response.completion_text.strip() + "\n" +
                    "═"*20
                )
                await asyncio.sleep(1)
        except Exception as e:
            yield event.plain_result(f"💥 战场崩溃：{str(e)}")
        
        endings = [
            ("双方战至平手","https://img1.baidu.com/it/u=2045001711,1644967445&fm=253&fmt=auto&app=138&f=JPEG?w=638&h=359"),
            ("右脑胜利","https://img0.baidu.com/it/u=3860935722,587125014&fm=253&fmt=auto&app=138&f=JPEG?w=800&h=1422"),
            ("左脑反败为胜","https://img2.baidu.com/it/u=3723802084,4111467673&fm=253&fmt=auto&app=138&f=JPEG?w=800&h=1103")
        ]
        end_text, end_img = random.choice(endings)
        ending_image = await self.safe_send_image(end_img)
        yield event.chain_result([
            ending_image or Plain("🎲"),
            Plain(f"\n🏁 最终结果：{end_text}")
        ])

    async def terminate(self):
        pass

class help(Star):
    def __init__(self, context: Context, config: dict):
        super().__init__(context)
        self.config = config  # 插件配置

    @filter.command("meaning帮助")
    async def helloworld(self, event: AstrMessageEvent):
        if not self.config.get("enable_help_command", True):
            yield event.plain_result("帮助功能已关闭")
            return
        user_name = event.get_sender_name()
        message_str = event.message_str
        yield event.plain_result(f"Hello, {user_name}!\n支持搜所 搜索+关键词\n天气查询 天气+关键词\n星座查询 星座运势+白羊座\n两个Emoji合成，例如：合成 🤯😭\n支持搜图 来点 关键词 格式\n蔡徐坤 / 来点坤图 - 蔡徐坤图片\腹肌  \n 原神黄历 / 来点骚的 - 原神黄历 \n 热榜 - 今日热榜 \n 小动物 - 可爱动物 \n 看看妞 - 随机美女 \n 看看腿 - 腿部特写 \n 猫猫 - 治愈猫咪 \n 风景 / 景色 - 4K 风景 \n 随便来点 - 随机图片\n doro结局  \n三坑少女\n 求签 - 每日运势 \n 点阵字 [内容] [符号] - 生成点阵字（例：点阵字 你好 好）\nhello 七七温馨提示少看腿有助于身心健康")

class ArknightsPlugin(Star):
    def __init__(self, context: Context, config: dict):
        super().__init__(context)
        self.config = config  # 插件配置

    @event_message_type(EventMessageType.ALL)
    async def on_message(self, event: AstrMessageEvent) -> MessageEventResult:
        if not self.config.get("enable_image_features", True):
            return
        
        user_id = event.get_sender_id()
        group_id = event.get_group_id()

        def check_whitelist_blacklist():
            if self.config["allow_users"] and user_id not in self.config["allow_users"]:
                return False
            if user_id in self.config["deny_users"]:
                return False
            if group_id and self.config["allow_groups"] and group_id not in self.config["allow_groups"]:
                return False
            if group_id and group_id in self.config["deny_groups"]:
                return False
            return True

        if not check_whitelist_blacklist():
            return

        try:
            msg_obj = event.message_obj
            text = msg_obj.message_str or ""
            logger.debug("=== Debug: AstrBotMessage ===")
            for attr in ['self_id', 'session_id', 'message_id', 'sender', 'group_id', 'message', 'raw_message', 'timestamp']:
                logger.debug(f"{attr.capitalize()}: {getattr(msg_obj, attr)}")
            logger.debug("=================")
            async with aiohttp.ClientSession() as session:

                # 原神黄历/来点骚的
                if "原神黄历" in text or "来点骚的" in text:
                    if not self.config.get("enable_yuanshen_calendar", True):
                        return
                    beauty_api_url = "https://api.xingzhige.com/API/yshl/"
                    try:
                        async with session.get(beauty_api_url) as response:  # 异步请求
                            content = await response.read()  # 读取内容
                            local_image_path = "temp_beauty_image.jpg"
                            with open(local_image_path, 'wb') as f:
                                f.write(content)
                            yield event.make_result().file_image(local_image_path)
                            if os.path.exists(local_image_path):
                                os.remove(local_image_path)
                    except aiohttp.ClientError as e:  # 捕获 aiohttp 异常
                        logger.error(f"请求图片链接 {beauty_api_url} 时出错: {e}")
                        yield event.plain_result("抱歉，暂时无法获取美女图片，请稍后再试。")

                # 热榜
                elif "热榜" in text:
                    if not self.config.get("enable_hot_list", True):
                        return
                    beauty_api_url = "https://api.317ak.com/API/yljk/60s/60s.php"
                    try:
                        async with session.get(beauty_api_url) as response:
                            content = await response.read()
                            local_image_path = "temp_rebang_image.jpg"
                            with open(local_image_path, 'wb') as f:
                                f.write(content)
                            yield event.make_result().file_image(local_image_path)
                            if os.path.exists(local_image_path):
                                os.remove(local_image_path)
                    except aiohttp.ClientError as e:
                        logger.error(f"请求图片链接 {beauty_api_url} 时出错: {e}")
                        yield event.plain_result("抱歉，暂时无法获取美女图片，请稍后再试。")

                # 小动物
                elif "小动物" in text:
                    if not self.config.get("enable_animal_images", True):
                        return
                    beauty_api_url = "https://api.pearktrue.cn/api/animal/?type=image&anime=dog"
                    try:
                        async with session.get(beauty_api_url) as response:
                            content = await response.read()
                            local_image_path = "temp_hjm_image.jpg"
                            with open(local_image_path, 'wb') as f:
                                f.write(content)
                            yield event.make_result().file_image(local_image_path)
                            if os.path.exists(local_image_path):
                                os.remove(local_image_path)
                    except aiohttp.ClientError as e:
                        logger.error(f"请求图片链接 {beauty_api_url} 时出错: {e}")
                        yield event.plain_result("抱歉，暂时无法获取美女图片，请稍后再试。")

                # 三坑少女
                elif "三坑少女" in text:
                    if not self.config.get("enable_sankens_images", True):
                        return
                    beauty_api_url = "https://api.pearktrue.cn/api/beautifulgirl/?type=image"
                    try:
                        async with session.get(beauty_api_url) as response:
                            content = await response.read()
                            local_image_path = "temp_sanken_image.jpg"
                            with open(local_image_path, 'wb') as f:
                                f.write(content)
                            yield event.make_result().file_image(local_image_path)
                            if os.path.exists(local_image_path):
                                os.remove(local_image_path)
                    except aiohttp.ClientError as e:
                        logger.error(f"请求图片链接 {beauty_api_url} 时出错: {e}")
                        yield event.plain_result("抱歉，暂时无法获取美女图片，请稍后再试。")

                # 看看妞
                elif "看看妞" in text:
                    if not self.config.get("enable_see_niuniu_images", True):
                        return
                    beauty_api_url = "https://free.wqwlkj.cn/wqwlapi/ks_xjj.php?type=image"
                    try:
                        async with session.get(beauty_api_url) as response:
                            content = await response.read()
                            local_image_path = "temp_niu_image.jpg"
                            with open(local_image_path, 'wb') as f:
                                f.write(content)
                            yield event.make_result().file_image(local_image_path)
                            if os.path.exists(local_image_path):
                                os.remove(local_image_path)
                    except aiohttp.ClientError as e:
                        logger.error(f"请求图片链接 {beauty_api_url} 时出错: {e}")
                        yield event.plain_result("抱歉，暂时无法获取美女图片，请稍后再试。")

                # 猫猫
                elif "猫猫" in text:
                    if not self.config.get("enable_cat_images", True):
                        return
                    beauty_api_url = "http://110.40.70.113:25514/API/maoyuna"
                    try:
                        async with session.get(beauty_api_url) as response:
                            content = await response.read()
                            local_image_path = "temp_mimi_image.jpg"
                            with open(local_image_path, 'wb') as f:
                                f.write(content)
                            yield event.make_result().file_image(local_image_path)
                            if os.path.exists(local_image_path):
                                os.remove(local_image_path)
                    except aiohttp.ClientError as e:
                        logger.error(f"请求图片链接 {beauty_api_url} 时出错: {e}")
                        yield event.plain_result("抱歉，暂时无法获取美女图片，请稍后再试。")

                # 风景/景色
                elif "风景" in text or "景色" in text:
                    if not self.config.get("enable_scenery_images", True):
                        return
                    beauty_api_url = "http://api.xingchenfu.xyz/API/cgq4kjsdt.php"
                    try:
                        async with session.get(beauty_api_url) as response:
                            content = await response.read()
                            local_image_path = "temp_jing_image.jpg"
                            with open(local_image_path, 'wb') as f:
                                f.write(content)
                            yield event.make_result().file_image(local_image_path)
                            if os.path.exists(local_image_path):
                                os.remove(local_image_path)
                    except aiohttp.ClientError as e:
                        logger.error(f"请求图片链接 {beauty_api_url} 时出错: {e}")
                        yield event.plain_result("抱歉，暂时无法获取美女图片，请稍后再试。")

                # 随便来点
                elif "随便来点" in text:
                    if not self.config.get("enable_random_images", True):
                        return
                    beauty_api_url = "http://api.xingchenfu.xyz/API/tu.php"
                    try:
                        async with session.get(beauty_api_url) as response:
                            content = await response.read()
                            local_image_path = "temp_sb_image.jpg"
                            with open(local_image_path, 'wb') as f:
                                f.write(content)
                            yield event.make_result().file_image(local_image_path)
                            if os.path.exists(local_image_path):
                                os.remove(local_image_path)
                    except aiohttp.ClientError as e:
                        logger.error(f"请求图片链接 {beauty_api_url} 时出错: {e}")
                        yield event.plain_result("抱歉，暂时无法获取美女图片，请稍后再试。")

                # 龙图
                elif "龙图" in text:
                    if not self.config.get("enable_long_images", True):
                        return
                    beauty_api_url = "http://api.xingchenfu.xyz/API/long.php"
                    try:
                        async with session.get(beauty_api_url) as response:
                            content = await response.read()
                            local_image_path = "temp_long_image.jpg"
                            with open(local_image_path, 'wb') as f:
                                f.write(content)
                            yield event.make_result().file_image(local_image_path)
                            if os.path.exists(local_image_path):
                                os.remove(local_image_path)
                    except aiohttp.ClientError as e:
                        logger.error(f"请求图片链接 {beauty_api_url} 时出错: {e}")
                        yield event.plain_result("抱歉，暂时无法获取美女图片，请稍后再试。")

                # cosplay/来点cos
                elif "cosplay" in text or "来点cos" in text:
                    if not self.config.get("enable_cosplay_images", True):
                        return
                    beauty_api_url = "http://api.xingchenfu.xyz/API/cosplay.php"
                    try:
                        async with session.get(beauty_api_url) as response:
                            content = await response.read()
                            local_image_path = "temp_cos_image.jpg"
                            with open(local_image_path, 'wb') as f:
                                f.write(content)
                            yield event.make_result().file_image(local_image_path)
                            if os.path.exists(local_image_path):
                                os.remove(local_image_path)
                    except aiohttp.ClientError as e:
                        logger.error(f"请求图片链接 {beauty_api_url} 时出错: {e}")
                        yield event.plain_result("抱歉，暂时无法获取美女图片，请稍后再试。")

                # 来点二次元
                elif "来点二次元" in text:
                    if not self.config.get("enable_erciyuan_images", True):
                        return
                    beauty_api_url = "http://api.xingchenfu.xyz/API/ecy.php"
                    try:
                        async with session.get(beauty_api_url) as response:
                            content = await response.read()
                            local_image_path = "temp_erciyuan_image.jpg"
                            with open(local_image_path, 'wb') as f:
                                f.write(content)
                            yield event.make_result().file_image(local_image_path)
                            if os.path.exists(local_image_path):
                                os.remove(local_image_path)
                    except aiohttp.ClientError as e:
                        logger.error(f"请求图片链接 {beauty_api_url} 时出错: {e}")
                        yield event.plain_result("抱歉，暂时无法获取美女图片，请稍后再试。")

                # 海贼王
                elif "海贼王" in text:
                    if not self.config.get("enable_onepiece_images", True):
                        return
                    beauty_api_url = "http://api.xingchenfu.xyz/API/haizeiwang.php"
                    try:
                        async with session.get(beauty_api_url) as response:
                            content = await response.read()
                            local_image_path = "temp_haizw_image.jpg"
                            with open(local_image_path, 'wb') as f:
                                f.write(content)
                            yield event.make_result().file_image(local_image_path)
                            if os.path.exists(local_image_path):
                                os.remove(local_image_path)
                    except aiohttp.ClientError as e:
                        logger.error(f"请求图片链接 {beauty_api_url} 时出错: {e}")
                        yield event.plain_result("抱歉，暂时无法获取美女图片，请稍后再试。")

                # 蜡笔小新
                elif "蜡笔小新" in text:
                    if not self.config.get("enable_luxun_images", True):
                        return
                    beauty_api_url = "http://api.xingchenfu.xyz/API/labixiaoxin.php"
                    try:
                        async with session.get(beauty_api_url) as response:
                            content = await response.read()
                            local_image_path = "temp_nabixiaoxin_image.jpg"
                            with open(local_image_path, 'wb') as f:
                                f.write(content)
                            yield event.make_result().file_image(local_image_path)
                            if os.path.exists(local_image_path):
                                os.remove(local_image_path)
                    except aiohttp.ClientError as e:
                        logger.error(f"请求图片链接 {beauty_api_url} 时出错: {e}")
                        yield event.plain_result("抱歉，暂时无法获取美女图片，请稍后再试。")

                # doro结局
                elif "doro结局" in text:
                    if not self.config.get("enable_doro_images", True):
                        return
                    beauty_api_url = "http://110.40.70.113:25514/API/sjdojieju"
                    try:
                        async with session.get(beauty_api_url) as response:
                            content = await response.read()
                            local_image_path = "temp_doro_image.jpg"
                            with open(local_image_path, 'wb') as f:
                                f.write(content)
                            yield event.make_result().file_image(local_image_path)
                            if os.path.exists(local_image_path):
                                os.remove(local_image_path)
                    except aiohttp.ClientError as e:
                        logger.error(f"请求图片链接 {beauty_api_url} 时出错: {e}")
                        yield event.plain_result("抱歉，暂时无法获取美女图片，请稍后再试。")

                # 早安/晚安
                elif "早安" in text or "晚安" in text:
                    if not self.config.get("enable_greetings_images", True):
                        return
                    beauty_api_url = "https://api.317ak.com/API/tp/zawa.php"
                    try:
                        async with session.get(beauty_api_url) as response:
                            content = await response.read()
                            local_image_path = "temp_hello_image.jpg"
                            with open(local_image_path, 'wb') as f:
                                f.write(content)
                            yield event.make_result().file_image(local_image_path)
                            if os.path.exists(local_image_path):
                                os.remove(local_image_path)
                    except aiohttp.ClientError as e:
                        logger.error(f"请求图片链接 {beauty_api_url} 时出错: {e}")
                        yield event.plain_result("抱歉，暂时无法获取美女图片，请稍后再试。")

                # 历史上的今天
                elif "历史上的今天" in text:
                    if not self.config.get("enable_history_today", True):
                        return
                    beauty_api_url = "https://api.317ak.com/API/qtapi/lssdjt/lssdjt.php"
                    try:
                        async with session.get(beauty_api_url) as response:
                            content = await response.read()
                            local_image_path = "temp_jt_image.jpg"
                            with open(local_image_path, 'wb') as f:
                                f.write(content)
                            yield event.make_result().file_image(local_image_path)
                            if os.path.exists(local_image_path):
                                os.remove(local_image_path)
                    except aiohttp.ClientError as e:
                        logger.error(f"请求图片链接 {beauty_api_url} 时出错: {e}")
                        yield event.plain_result("抱歉，暂时无法获取美女图片，请稍后再试。")

                # 腹肌
                elif "腹肌" in text:
                    if not self.config.get("enable_abs_images", True):
                        return
                    beauty_api_url = "https://api.317ak.com/API/tp/fjtp.php"
                    try:
                        async with session.get(beauty_api_url) as response:
                            content = await response.read()
                            local_image_path = "temp_fj_image.jpg"
                            with open(local_image_path, 'wb') as f:
                                f.write(content)
                            yield event.make_result().file_image(local_image_path)
                            if os.path.exists(local_image_path):
                                os.remove(local_image_path)
                    except aiohttp.ClientError as e:
                        logger.error(f"请求图片链接 {beauty_api_url} 时出错: {e}")
                        yield event.plain_result("抱歉，暂时无法获取美女图片，请稍后再试。")

                # 来点原神
                elif "来点原神" in text:
                    if not self.config.get("enable_ys_images", True):
                        return
                    beauty_api_url = "https://api.317ak.com/API/tp/ystp.php"
                    try:
                        async with session.get(beauty_api_url) as response:
                            content = await response.read()
                            local_image_path = "temp_ys_image.jpg"
                            with open(local_image_path, 'wb') as f:
                                f.write(content)
                            yield event.make_result().file_image(local_image_path)
                            if os.path.exists(local_image_path):
                                os.remove(local_image_path)
                    except aiohttp.ClientError as e:
                        logger.error(f"请求图片链接 {beauty_api_url} 时出错: {e}")
                        yield event.plain_result("抱歉，暂时无法获取美女图片，请稍后再试。")

                # 求签
                elif "求签" in text or "抽签" in text or "今日运势" in text:
                    if not self.config.get("enable_qiuqian", True):
                        return
                    qian_url = "https://www.hhlqilongzhu.cn/api/yl_qiuqian.php"
                    try:
                        async with session.get(qian_url, params={"type": "text"}) as resp:
                            # 1. 基础校验
                            if resp.status != 200:
                                raise ValueError(f"请求失败，状态码：{resp.status}")
                            
                            # 2. 获取原始文本（关键修复）
                            raw_text = await resp.text()
                            if not raw_text.strip():
                                raise ValueError("空空如也的签筒，要不要再试一次？")
                            
                            # 3. 智能解析签文（兼容新旧格式）
                            qian_pattern = r'「签诗」(.*?)「解签」(.*)'
                            match = re.search(qian_pattern, raw_text, re.DOTALL)
                            
                            if not match:
                                # 兼容旧格式（无「签诗」前缀）
                                parts = [p.strip() for p in raw_text.split('「') if p.strip()]
                                if len(parts) >= 2:
                                    qian_shi = parts[0].replace('解签', '').strip()
                                    jie_qian = parts[1].replace('」', '').strip()
                                else:
                                    raise ValueError("奇怪的签文格式，可能是神仙在玩捉迷藏~")
                            else:
                                qian_shi, jie_qian = match.groups()
                            
                            # 4. 格式美化（活跃气氛）
                            result = (
                                f"✨ 【今日灵签】✨\n"
                                f"⛩️ 签诗：{qian_shi}\n\n"
                                f"🔮 解签：{jie_qian}\n"
                                f"（点击头像再求一签，说不定会有惊喜哦~）"
                            ).replace('，', '，\n').replace('。', '。\n')  # 增强断句可读性
                            
                            yield event.plain_result(result)
                            
                    except (aiohttp.ClientError, ValueError) as e:
                        logger.warning(f"求签失败：{str(e)}，原始响应：{await resp.text()[:200]}")
                        yield event.plain_result(
                            "🌪️ 签筒被妖风打乱啦！\n"
                            "再摇一次试试？(≧∇≦)ﾉ"
                        )

                # 你喜欢我吗
                elif "你喜欢我吗" in text:
                    yield event.plain_result("https://file.tangdouz.com/love/")

                # ciallo
                elif "ciallo" in text:
                    yield event.plain_result("http://file.tangdouz.com/ciallo/")

                # 每日日报
                elif "每日日报" in text:
                    if not self.config.get("enable_daily_report", True):
                        return
                    api_url = "https://api.tangdouz.com/a/60/"
                    try:
                        async with session.get(api_url, params={"return": "json"}) as response:
                            # 核心修复：跳过Content-Type校验，直接尝试解析JSON
                            raw_content = await response.text()
                            try:
                                data = json.loads(raw_content)
                            except json.JSONDecodeError:
                                raise ValueError("内容非JSON格式")  # 真正的非JSON错误
                            
                            # 校验数据完整性（不管响应头是否正确）
                            if not all(key in data for key in ["url", "music"]):
                                raise ValueError("缺少必要字段：url/music")
                            
                            # 直接发送网络图片（AstrBot支持URL直传）
                            yield event.image_result(data["url"])
                            yield event.plain_result(f"🎵 今日BGM：{data['music']}")
                            
                    except json.JSONDecodeError:  # 真正的JSON解析失败（如乱码）
                        logger.error(f"日报内容解析失败：{raw_content[:200]}")
                        yield event.plain_result("📄 日报数据损坏，点击重试刷新~")
                    except aiohttp.ClientError as e:  # 网络错误
                        logger.error(f"日报请求失败：{e}")
                        yield event.plain_result("🌐 加载日报时遇到网络波动，请稍后再试~")
                    except ValueError as e:  # 数据校验失败
                        logger.error(f"日报数据异常：{e}")
                        yield event.plain_result(f"⚠️ 日报内容有误：{str(e)}")
                # 点阵字
                elif "点阵字" in text:
                    if not self.config.get("enable_diandianzi", True):
                        return
                    try:
                        parts = text.split()
                        if len(parts) < 3:
                            raise ValueError("输入格式应为：点阵字 要转换的字 填充字")
                        msg = parts[1]
                        fill = parts[2]
                        api_url = "https://api.lolimi.cn/API/dzz/api.php"
                        params = {"msg": msg, "fill": fill}
                        async with session.get(api_url, params=params) as response:
                            data = await response.json()
                            code = data.get("code")
                            if code == 1:
                                result = data.get("data", "")
                                yield event.plain_result(f".\n{result}")
                            else:
                                yield event.plain_result("抱歉，获取点阵字失败，请稍后再试。")
                    except aiohttp.ClientError as e:
                        logger.error(f"请求点阵字 API 链接 {api_url} 时出错: {e}")
                        yield event.plain_result("抱歉，暂时无法获取点阵字，请稍后再试。")
                    except ValueError as e:
                        logger.error(f"输入格式错误: {e}")
                        yield event.plain_result(str(e))

                # 弔图
                # elif "弔图" in text:
                #     if not self.config.get("enable_bang_images", True):
                #         return
                #     beauty_api_url = "https://cyapi.top/yz/dt.php"
                #     try:
                #         async with session.get(beauty_api_url) as response:
                #             content = await response.read()
                #             local_image_path = "temp_diao_image.jpg"
                #             with open(local_image_path, 'wb') as f:
                #                 f.write(content)
                #             yield event.make_result().file_image(local_image_path)
                #             if os.path.exists(local_image_path):
                #                 os.remove(local_image_path)
                #     except aiohttp.ClientError as e:
                #         logger.error(f"请求图片链接 {beauty_api_url} 时出错: {e}")
                #         yield event.plain_result("抱歉，暂时无法获取美女图片，请稍后再试。")

                # 看看腿
                elif "看看腿" in text:
                    if not self.config.get("enable_look_leg_images", True):
                        return
                    api_url = "https://api.lolimi.cn/API/meizi/api.php"
                    temp_path = "temp_meizi_image.jpg"
                    try:
                        async with session.get(api_url) as response:
                            data = await response.json()
                            if data.get("code") == 1:
                                image_url = data["text"]
                                async with session.get(image_url) as img_response:
                                    img_content = await img_response.read()
                                    with open(temp_path, 'wb') as f:
                                        f.write(img_content)
                                    yield event.make_result().file_image(temp_path)
                            else:
                                yield event.plain_result(f"图片获取失败（状态码: {data.get('code')}）")
                    except aiohttp.ClientError as e:
                        logger.error(f"请求图片出错: {e}")
                        yield event.plain_result("抱歉，暂时无法获取图片，请稍后再试。")
                    finally:
                        if os.path.exists(temp_path):
                            os.remove(temp_path)

                # 蔡徐坤/来点坤图
                elif "蔡徐坤" in text or "来点坤图" in text:
                    if not self.config.get("enable_cai_xukun_images", True):
                        return
                    api_url = "https://api.tangdouz.com/zzz/kk.php"
                    temp_path = "temp_kk_image.jpg"
                    try:
                        async with session.get(api_url) as response:
                            image_url = await response.text()  # 获取文本响应
                            async with session.get(image_url.strip()) as img_response:
                                img_content = await img_response.read()
                                with open(temp_path, 'wb') as f:
                                    f.write(img_content)
                                yield event.make_result().file_image(temp_path)
                    except aiohttp.ClientError as e:
                        logger.error(f"请求随机坤坤表情包失败: {e}")
                        yield event.plain_result("抱歉，坤坤表情包加载失败，请稍后再试~")
                    finally:
                        if os.path.exists(temp_path):
                            os.remove(temp_path)

                # 来点
                elif "来点" in text:
                    if not self.config.get("enable_dtss_images", True):
                        return
                    search_keyword = text.replace("来点", "").strip()
                    if not search_keyword:
                        yield event.plain_result("请输入搜索关键词，例如：来点 动漫")
                        return
                    api_url = f"https://api.tangdouz.com/dtss.php?nr={search_keyword}"
                    temp_path = f"temp_dtss_image_{search_keyword}.jpg"
                    try:
                        async with session.get(api_url) as response:
                            image_url = await response.text()
                            image_url =image_url.strip()
                            async with session.get(image_url) as img_response:
                                img_content = await img_response.read()
                                with open(temp_path, 'wb') as f:
                                    f.write(img_content)
                                yield event.make_result().file_image(temp_path)
                    except aiohttp.ClientError as e:
                        logger.error(f"堆糖搜索请求失败（关键词：{search_keyword}）: {e}")
                        yield event.plain_result(f"抱歉，搜索“{search_keyword}”图片失败，请稍后再试~")
                    finally:
                        if os.path.exists(temp_path):
                            os.remove(temp_path)

                # 搜索/bing搜索
                elif text.startswith("搜索") or "bing搜索" in text:
                    if not self.config.get("enable_bing_search", True):
                        return
                    keyword = text.replace("搜索", "").replace(" bing搜索", "").strip()
                    if not keyword:
                        yield event.plain_result("❓ 请输入搜索关键词，例如：/搜索 人工智能")
                        return
                    search_url = f"https://api.pearktrue.cn/api/bingsearch/?search={keyword}"
                    try:
                        async with session.get(search_url, timeout=10) as response:
                            result = await response.json()
                            if result["code"] != 200:
                                yield event.plain_result(f"🔍 搜索失败：{result.get('msg', '未知错误')}")
                                return
                            chat_records = [f"📢 搜索关键词：{keyword}\n"]
                            for idx, item in enumerate(result["data"], 1):
                                chat_records.append(f"【第{idx}条结果】")
                                chat_records.append(f"💬 标题：{item['title']}")
                                chat_records.append(f"📝 摘要：{item['abstract'][:]}")
                                chat_records.append(f"🔗 链接：\n{item['href']}\n")
                            yield event.plain_result("\n".join(chat_records))
                    except aiohttp.ClientError as e:
                        logger.error(f"Bing搜索请求失败：{e}")
                        yield event.plain_result("🔍 网络请求超时，请检查网络后重试~")
                    except ValueError:
                        logger.error(f"Bing搜索数据解析失败：{await response.text()}")
                        yield event.plain_result("🔍 数据格式错误，可能是API返回异常")

                # 天气查询
                elif text.startswith("天气") or " 天气查询" in text:
                    if not self.config.get("enable_weather_query", True):
                        return
                    city = text.replace("天气", "").replace("天气查询", "").strip()
                    if not city:
                        yield event.plain_result("🌤️ 请输入城市名称，例如：天气 深圳")
                        return
                    api_url = f"https://api.tangdouz.com/tq.php?dz={city}&return=json"
                    try:
                        async with session.get(api_url, timeout=10) as response:
                            result = await response.json()
                            if not result.get("city"):
                                yield event.plain_result(f"🌍 未找到城市：{city} 的天气信息")
                                return
                            weather_info = [
                                f"🌆 城市：{result['city']}",
                                "—— 未来三天天气预报 ——"
                            ]
                            for day in range(1, 4):
                                data = result.get(str(day), {})
                                weather_info.append(
                                    f"📅 {data.get('date', '未知日期')}\n"
                                    f"🌞 天气：{data.get('weather', '未知天气')}\n"
                                    f"温度：{data.get('low', '?')} ~ {data.get('high', '?')}"
                                )
                            yield event.plain_result("\n".join(weather_info))
                    except aiohttp.ClientError as e:
                        logger.error(f"天气API请求失败：{e}")
                        yield event.plain_result("🌐 网络请求超时，请检查城市名称或重试~")

                # 星座运势
                elif text.startswith("星座运势") or " 星座运势查询" in text:
                    if not self.config.get("enable_astrology_image", True):
                        return
                    constellation = text.replace("星座运势", "").replace(" 星座运势查询", "").strip()
                    if not constellation:
                        yield event.plain_result("🌠 请输入星座名称，例如：星座运势 白羊座")
                        return
                    api_url = f"https://api.317ak.com/API/qtapi/xzys/xzys.php?msg={constellation}"
                    temp_image_path = f"temp_astrology_{constellation}.jpg"
                    try:
                        async with session.get(api_url, timeout=15) as response:
                            content_type = response.headers.get("Content-Type", "")
                            if not content_type.startswith("image/"):
                                yield event.plain_result(f"❌ 接口返回异常，状态码：{response.status}")
                                return
                            content = await response.read()
                            with open(temp_image_path, "wb") as f:
                                f.write(content)
                            yield event.make_result().file_image(temp_image_path)
                    except aiohttp.ClientError as e:
                        logger.error(f"星座运势API请求失败：{e}")
                        yield event.plain_result("🌐 网络请求超时，请检查星座名称或重试~")
                    finally:
                        if os.path.exists(temp_image_path):
                            os.remove(temp_image_path)

                # 合成Emoji
                elif text.startswith("合成"):
                    if not self.config.get("enable_emoji_mix", True):
                        return
                    emojis = re.findall(
                        r'[\U0001F600-\U0001F9FF\u263a-\U0001F645]',
                        text[2:]
                    )
                    emoji1, emoji2 = emojis[:2]
                    api_url = f"https://oiapi.net/API/EmojiMix/{emoji1}/{emoji2}"
                    try:
                        async with session.get(api_url, timeout=10) as response:
                            result = await response.json()
                            if result["code"] != 1:
                                yield event.plain_result("合成失败，请检查Emoji输入")
                                return
                            image_url = result["data"].get("url")
                            if not image_url:
                                yield event.plain_result(f"ℹ️ 文本结果：{result['data']}")
                                return
                            local_image = await download_image_by_url(image_url)
                            if local_image:
                                yield event.make_result().file_image(local_image)
                            else:
                                yield event.plain_result(
                                    f"🎨 Emoji合成结果：\n"
                                    f"{emoji1} + {emoji2} =\n"
                                    f"查看合成图片：{image_url}"
                                )
                    except aiohttp.ClientError as e:
                        logger.error(f"Emoji合成API请求失败：{e}")

        except Exception as e:
            logger.error(f"处理消息时发生未知错误: {e}")
            yield event.plain_result("哎呀，出现了一个错误，请稍后再试。")
