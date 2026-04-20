import sqlite3
import re

db_file = r'D:\work\OneDrive\Desktop\projects\zhejiangzhiyuan\gaokao_system\data\gaokao_integrated.db'

# 就业网站数据（从GitHub仓库提取）
career_websites = [
    # 四川
    ('四川', '西南交通大学', 'http://jiuye.swjtu.edu.cn/eweb/jygl/zpfw.so'),
    ('四川', '电子科技大学', 'http://jiuye.uestc.edu.cn/career/index.html'),
    ('四川', '四川大学', 'http://jy.scu.edu.cn/eweb/jygl/index.so'),
    ('四川', '西南财经大学', 'https://jobzpgl.swufe.edu.cn/'),
    ('四川', '西南民族大学', 'http://jy.swun.edu.cn/Website/'),
    ('四川', '成都理工大学', 'http://www.jy.cdut.edu.cn/'),
    ('四川', '西南科技大学', 'http://job.swust.edu.cn/'),
    ('四川', '四川农业大学', 'http://job.sicau.edu.cn/'),
    ('四川', '成都中医药大学', 'http://zsjy.cdutcm.edu.cn/'),
    ('四川', '四川师范大学', 'http://jy.sicnu.edu.cn/'),
    ('四川', '西华师范大学', 'https://job.cwnu.edu.cn/'),
    ('四川', '四川轻化工大学', 'http://job.suse.edu.cn/'),
    ('四川', '成都信息工程大学', 'http://cuit.njcdata.com/eweb/login.jsp'),
    ('四川', '西南医科大学', 'https://jy.swmu.edu.cn/'),
    ('四川', '成都医学院', 'http://jy.cmc.edu.cn/search/query.action?partId=3'),
    ('四川', '川北医学院', 'http://career.nsmc.edu.cn/'),
    ('四川', '内江师范学院', 'http://njtc.university-hr.cn/'),
    ('四川', '四川警察学院', 'http://jy.scpolicec.edu.cn/'),
    ('四川', '四川音乐学院', 'http://www.sccm.cn/erl/index.asp'),
    ('四川', '四川传媒学院', 'http://jy.cdysxy.com/'),
    ('四川', '成都文理学院', 'http://jyw.cdcas.edu.cn/NewNews/2004'),
    # 重庆
    ('重庆', '重庆大学', 'http://www.job.cqu.edu.cn/'),
    ('重庆', '西南大学', 'http://bkjyw.swu.edu.cn/'),
    ('重庆', '重庆交通大学', 'http://zsjy.cqjtu.edu.cn/jyw/Default.aspx'),
    ('重庆', '重庆邮电大学', 'http://job.cqupt.edu.cn/portal/home.html'),
    ('重庆', '重庆医科大学', 'http://cqmu.bysjy.com.cn/'),
    ('重庆', '重庆师范大学', 'http://job.cqnu.edu.cn/eweb/jygl/index.so'),
    ('重庆', '重庆工商大学', 'https://www.ctbu.edu.cn/jobi/default.html#/index'),
    ('重庆', '西南政法大学', 'http://swupl.jysd.com/'),
    ('重庆', '重庆科技大学', 'http://cqust.bysjy.com.cn/'),
    ('重庆', '重庆理工大学', 'http://jyxt.i.cqut.edu.cn/type_pr/00001010303.html'),
    ('重庆', '长江师范学院', 'http://yznu.bysjy.com.cn/'),
    ('重庆', '四川外国语大学', 'http://column.sisu.edu.cn/cwjyw/index.htm'),
    ('重庆', '四川美术学院', 'http://www.scfai.edu.cn/jy/dxsjy/xjhxx.htm'),
    # 北京
    ('北京', '北京大学', 'https://scc.pku.edu.cn/home!recruitList.action?category=1'),
    ('北京', '中国人民大学', 'http://rdjy.ruc.edu.cn/'),
    ('北京', '清华大学', 'http://career.tsinghua.edu.cn/'),
    ('北京', '北京科技大学', 'http://job.ustb.edu.cn/'),
    ('北京', '北京交通大学', 'https://job.bjtu.edu.cn/cms/notice/'),
    ('北京', '中国石油大学(北京)', 'http://career.cup.edu.cn/'),
    ('北京', '中国矿业大学(北京)', 'http://jy.cumtb.edu.cn/'),
    ('北京', '中国地质大学(北京)', 'http://jiuye.cugb.edu.cn/'),
    ('北京', '北京邮电大学', 'https://job.bupt.edu.cn/'),
    ('北京', '华北电力大学', 'http://job.ncepu.edu.cn/'),
    ('北京', '北京化工大学', 'http://www.job.buct.edu.cn/'),
    ('北京', '北京林业大学', 'http://job.bjfu.edu.cn/frontpage/bjfu/html/index.html'),
    ('北京', '北京外国语大学', 'https://jyzd.bfsu.edu.cn/'),
    ('北京', '北京师范大学', 'http://career.bnu.edu.cn/front/channel.jspa?channelId=745&parentId=741'),
    ('北京', '北京中医药大学', 'http://jy.bucm.edu.cn/'),
    ('北京', '对外经济贸易大学', 'http://career.uibe.edu.cn/'),
    ('北京', '中央财经大学', 'http://scc.cufe.edu.cn/f/home/index/'),
    ('北京', '中国政法大学', 'http://career.cupl.edu.cn'),
    ('北京', '中央民族大学', 'http://www.career.muc.edu.cn/'),
    ('北京', '北京体育大学', 'http://jy.bsu.edu.cn/index.jspa'),
    ('北京', '北京航空航天大学', 'http://career.buaa.edu.cn/homePageAction.dhtml'),
    ('北京', '北京理工大学', 'http://job.bit.edu.cn/portal/home.html'),
    ('北京', '北京工商大学', 'http://gsbys.btbu.edu.cn/'),
    ('北京', '北京联合大学', 'https://jy.buu.edu.cn/'),
    ('北京', '首都医科大学', 'http://jy.ccmu.edu.cn/sites/p/01/index.jsp'),
    ('北京', '首都师范大学', 'https://jy.cnu.edu.cn/'),
    ('北京', '首都经济贸易大学', 'https://jy.cueb.edu.cn/'),
    ('北京', '中国传媒大学', 'http://jy.cuc.edu.cn/'),
    ('北京', '中央美术学院', 'http://cafa.jysd.com/'),
    ('北京', '北京石油化工学院', 'http://jobbipt.jysd.com/'),
    # 天津
    ('天津', '南开大学', 'http://career.nankai.edu.cn/'),
    ('天津', '天津大学', 'http://job.twtstudio.com/main'),
    ('天津', '天津工业大学', 'http://job.tjpu.edu.cn/'),
    ('天津', '天津科技大学', 'http://jy.tust.edu.cn/'),
    ('天津', '天津理工大学', 'http://jy.tjut.edu.cn/'),
    # 河北
    ('河北', '河北工业大学', 'http://career.hebut.edu.cn/'),
    ('河北', '华北理工大学', 'http://zsjyc.ncst.edu.cn/'),
    ('河北', '燕山大学', 'http://job.ysu.edu.cn/default.html'),
    ('河北', '河北科技大学', 'http://job.hebust.edu.cn/'),
    ('河北', '河北工程大学', 'http://jiuye.hebeu.edu.cn/'),
    ('河北', '石家庄铁道大学', 'http://stdu.bysjy.com.cn/module/careers?menu_id=13797'),
    # 山西
    ('山西', '太原理工大学', 'http://jiuye.tyut.edu.cn/'),
    ('山西', '山西大学', 'http://sxu.jysd.com/'),
    ('山西', '太原科技大学', 'http://job.tyust.edu.cn/'),
    # 辽宁
    ('辽宁', '大连医科大学', 'http://dmu.bysjy.com.cn/'),
    ('辽宁', '大连理工大学', 'http://202.118.65.2/app/index.html'),
    ('辽宁', '东北大学', 'http://job.neu.edu.cn/'),
    ('辽宁', '辽宁大学', 'http://job.lnu.edu.cn/'),
    ('辽宁', '大连海事大学', 'http://myjob.dlmu.edu.cn/portal/home.html'),
    ('辽宁', '大连大学', 'http://career.dlu.edu.cn/'),
    ('辽宁', '沈阳理工大学', 'http://zsjy.sylu.edu.cn/plus/list.php?tid=6'),
    ('辽宁', '中国医科大学', 'http://jy.cmu.edu.cn/'),
    ('辽宁', '大连海洋大学', 'http://job.dlou.edu.cn/'),
    ('辽宁', '沈阳医学院', 'http://symc.bysjy.com.cn/'),
    # 吉林
    ('吉林', '吉林大学', 'http://jdjyw.jlu.edu.cn/'),
    ('吉林', '延边大学', 'http://career.ybu.edu.cn/'),
    ('吉林', '长春大学', 'http://ccdx.bibibi.net/'),
    # 黑龙江
    ('黑龙江', '东北林业大学', 'http://job.nefu.edu.cn/'),
    ('黑龙江', '哈尔滨工业大学', 'http://job.hit.edu.cn/'),
    ('黑龙江', '哈尔滨工程大学', 'http://job.hrbeu.edu.cn/HrbeuJY/web'),
    ('黑龙江', '黑龙江大学', 'http://job.hlju.edu.cn/'),
    ('黑龙江', '东北农业大学', 'http://job.neau.edu.cn/'),
    # 上海
    ('上海', '复旦大学', 'https://career.fudan.edu.cn/'),
    ('上海', '同济大学', 'https://tj91.tongji.edu.cn/'),
    ('上海', '上海交通大学', 'http://www.job.sjtu.edu.cn/'),
    ('上海', '华东理工大学', 'https://career.ecust.edu.cn/'),
    ('上海', '东华大学', 'http://ejob.dhu.edu.cn/'),
    ('上海', '华东师范大学', 'https://career.ecnu.edu.cn/common/index.aspx'),
    ('上海', '上海外国语大学', 'http://career.shisu.edu.cn/'),
    ('上海', '上海财经大学', 'http://career.sufe.edu.cn//'),
    ('上海', '上海大学', 'http://zbb.shu.edu.cn/New/Index.aspx'),
    ('上海', '上海理工大学', 'https://91.usst.edu.cn/'),
    ('上海', '上海海事大学', 'http://job.shmtu.edu.cn/'),
    ('上海', '上海师范大学', 'http://shnu.jysd.com/'),
    ('上海', '上海音乐学院', 'https://xsc.shcmusic.edu.cn/category/stu/jyzp.html'),
    # 江苏
    ('江苏', '南京大学', 'http://job.nju.edu.cn/#!/home'),
    ('江苏', '东南大学', 'http://seu.91job.org.cn/'),
    ('江苏', '中国矿业大学', 'http://jyzd.cumt.edu.cn/'),
    ('江苏', '江南大学', 'http://zsjyc.jiangnan.edu.cn/'),
    ('江苏', '河海大学', 'http://hhu.91job.org.cn/'),
    ('江苏', '南京农业大学', 'http://njau.91job.org.cn/'),
    ('江苏', '中国药科大学', 'http://cpu.91job.org.cn/'),
    ('江苏', '南京理工大学', 'http://rczp.njust.edu.cn/'),
    ('江苏', '南京航空航天大学', 'http://job.nuaa.edu.cn/'),
    ('江苏', '苏州大学', 'http://suda.91job.org.cn/'),
    ('江苏', '南京师范大学', 'http://njnu.jysd.com/'),
    ('江苏', '扬州大学', 'http://yzu.91job.org.cn/'),
    ('江苏', '南京邮电大学', 'http://njupt.91job.org.cn/'),
    ('江苏', '南京信息工程大学', 'http://nuist.91job.org.cn/'),
    ('江苏', '江苏科技大学', 'http://just.91job.org.cn/'),
    ('江苏', '南京工业大学', 'http://njtech.91job.org.cn/'),
    ('江苏', '南京林业大学', 'http://njfu.91job.org.cn/'),
    ('江苏', '南京医科大学', 'http://njmu.91job.org.cn/'),
    ('江苏', '南京中医药大学', 'http://njucm.91job.org.cn/'),
    ('江苏', '江苏师范大学', 'http://jsnu.91job.org.cn/'),
    ('江苏', '南京财经大学', 'http://njue.91job.org.cn/'),
    # 浙江
    ('浙江', '浙江大学', 'http://www.career.zju.edu.cn/jyxt/jyweb/webIndex.zf'),
    ('浙江', '宁波大学', 'http://ndjy.nbu.edu.cn/'),
    ('浙江', '杭州电子科技大学', 'http://career.hdu.edu.cn/'),
    ('浙江', '浙江工业大学', 'http://zjut.jysd.com/'),
    ('浙江', '浙江师范大学', 'http://career.zjnu.edu.cn/'),
    ('浙江', '浙江工商大学', 'http://jyw.zjgsu.edu.cn/eweb/index.so'),
    ('浙江', '杭州师范大学', 'http://hznu.jysd.com/'),
    ('浙江', '浙江理工大学', 'http://jyb.zstu.edu.cn/'),
    ('浙江', '浙江中医药大学', 'http://job.zcmu.edu.cn/'),
    ('浙江', '温州大学', 'http://job.wzu.edu.cn/'),
    ('浙江', '中国计量大学', 'https://jyb.cjlu.edu.cn/'),
    ('浙江', '浙江农林大学', 'http://jy.zafu.edu.cn/'),
    ('浙江', '温州医科大学', 'http://job.wmu.edu.cn/'),
    ('浙江', '浙江音乐学院', 'http://www.zjcm.edu.cn/a/20191016/5525.shtml'),
    ('浙江', '浙江传媒学院', 'http://job.cuz.edu.cn/zh/web/14321/1'),
    # 安徽
    ('安徽', '合肥工业大学', 'http://gdjy.hfut.edu.cn/'),
    ('安徽', '安徽大学', 'http://www.job.ahu.edu.cn/'),
    ('安徽', '安徽工业大学', 'http://ahut.ahbys.com/Index.html'),
    ('安徽', '安徽医科大学', 'http://ahmu.bysjy.com.cn/'),
    ('安徽', '安徽师范大学', 'http://jyw.wjhyfwy.com/'),
    ('安徽', '安徽财经大学', 'http://aufe.ahbys.com/'),
    ('安徽', '淮北师范大学', 'http://www.chnu.edu.cn/Category_6724/Index.aspx'),
    ('安徽', '安徽中医药大学', 'http://jyxxw.ahtcm.edu.cn/'),
    # 福建
    ('福建', '厦门大学', 'https://jyzd.xmu.edu.cn/'),
    ('福建', '华侨大学', 'https://bys.hqu.edu.cn/'),
    ('福建', '福建农林大学', 'http://career.fafu.edu.cn/'),
    ('福建', '福州大学', 'http://www.fjrclh.com/'),
    ('福建', '集美大学', 'http://jyzd.jmu.edu.cn/'),
    ('福建', '福建医科大学', 'http://fjyk.bibibi.net/'),
    ('福建', '福建中医药大学', 'https://jyzd.fjtcm.edu.cn/'),
    ('福建', '厦门工学院', 'http://www.xit.edu.cn/zsw/jypd/'),
    # 江西
    ('江西', '华东交通大学', 'http://zjc.ecjtu.edu.cn/module/onlines?type_id=5'),
    ('江西', '江西理工大学', 'http://jxlg.bysjy.com.cn/'),
    ('江西', '南昌大学', 'http://jy.ncu.edu.cn/index'),
    ('江西', '江西师范大学', 'https://jy.jxnu.edu.cn/f/home/index/'),
    ('江西', '华东理工大学', 'http://jyb.ecut.edu.cn/'),
    ('江西', '江西财经大学', 'http://career.jxufe.edu.cn/'),
    ('江西', '南昌航空大学', 'http://jyw.nchu.edu.cn/'),
    ('江西', '南昌理工学院', 'https://nclgxy.xiaopinyun.com/'),
    # 山东
    ('山东', '山东大学', 'http://www.job.sdu.edu.cn/'),
    ('山东', '山东科技大学', 'http://career.sdust.edu.cn/'),
    ('山东', '青岛大学', 'https://job.qdu.edu.cn/'),
    ('山东', '山东理工大学', 'https://sdutjob.sdut.edu.cn/'),
    ('山东', '烟台大学', 'http://career.ytu.edu.cn/'),
    ('山东', '聊城大学', 'http://lcu.sdbys.com/'),
    ('山东', '青岛科技大学', 'http://job.qust.edu.cn/'),
    ('山东', '济南大学', 'http://career.ujn.edu.cn/'),
    ('山东', '山东建筑大学', 'http://sdjzu.bibibi.net/'),
    ('山东', '山东农业大学', 'http://jyzx.sdau.edu.cn/'),
    ('山东', '山东财经大学', 'http://job.sdufe.edu.cn/'),
    ('山东', '山东师范大学', 'http://www.career.sdnu.edu.cn/cms'),
    # 河南
    ('河南', '郑州大学', 'http://job.zzu.edu.cn/p/page/index.html'),
    ('河南', '河南科技大学', 'https://zjc.haust.edu.cn/index/jycyzdzx/jysy.htm'),
    ('河南', '河南理工大学', 'http://hpu.bysjy.com.cn/'),
    ('河南', '河南工业大学', 'http://job.haut.edu.cn/'),
    ('河南', '河南师范大学', 'http://jc.htu.edu.cn/p/page/index.html'),
    ('河南', '河南财经政法大学', 'http://job.huel.edu.cn/'),
    ('河南', '华北水利水电大学', 'http://jyxx.ncwu.edu.cn/ncwu/p/page/index.html'),
    ('河南', '河南中医药大学', 'http://job.hactcm.edu.cn/hactcm/p/page/index.html'),
    # 湖北
    ('湖北', '武汉大学', 'http://www.xsjy.whu.edu.cn/default.html'),
    ('湖北', '中南财经政法大学', 'http://jyzx.zuel.edu.cn/'),
    ('湖北', '华中科技大学', 'http://job.hust.edu.cn/'),
    ('湖北', '中国地质大学', 'http://cug.91wllm.com/'),
    ('湖北', '华中农业大学', 'http://hzau.91wllm.com/'),
    ('湖北', '中南民族大学', 'http://job.scuec.edu.cn/eweb/login.jsp'),
    ('湖北', '长江大学', 'http://yangtzeu.91wllm.com/'),
    ('湖北', '湖北大学', 'http://hubu.91wllm.com/'),
    ('湖北', '三峡大学', 'http://jy.ctgu.edu.cn/'),
    ('湖北', '武汉科技大学', 'http://wust.91wllm.com/'),
    ('湖北', '湖北工业大学', 'https://hbut.91wllm.com/'),
    ('湖北', '武汉工程大学', 'http://jyb.wit.edu.cn/'),
    ('湖北', '湖北中医药大学', 'http://hbtcm.91wllm.com/'),
    ('湖北', '武汉轻工大学', 'http://whpu.91wllm.com/'),
    ('湖北', '湖北师范大学', 'http://hbnu.91wllm.com/'),
    # 湖南
    ('湖南', '湖南大学', 'http://hnu.bysjy.com.cn/'),
    ('湖南', '中南大学', 'http://career.csu.edu.cn/'),
    ('湖南', '长沙理工大学', 'http://csust.bysjy.com.cn/'),
    ('湖南', '湖南师范大学', 'http://hnsf.bysjy.com.cn/'),
    ('湖南', '湖南科技大学', 'http://jy.hnust.edu.cn/'),
    ('湖南', '湘潭大学', 'http://jobs.xtu.edu.cn/index.php'),
    ('湖南', '南华大学', 'http://nhdx.bibibi.net/'),
    ('湖南', '湖南工业大学', 'http://job.hut.edu.cn/'),
    ('湖南', '湖南农业大学', 'http://jy.hunau.edu.cn/'),
    ('湖南', '湖南工商大学', 'http://job.hnuc.edu.cn/'),
    # 广东
    ('广东', '中山大学', 'http://career.sysu.edu.cn/'),
    ('广东', '华南理工大学', 'http://jyzx.6ihnep7.cas.scut.edu.cn/jyzx/'),
    ('广东', '汕头大学', 'http://gdc.stu.edu.cn/'),
    ('广东', '暨南大学', 'https://career.jnu.edu.cn/eweb/jygl/index.so'),
    ('广东', '深圳大学', 'http://job.szu.edu.cn/'),
    ('广东', '广东工业大学', 'http://job.gdut.edu.cn/unijob/index.php/web/Index/index'),
    ('广东', '华南农业大学', 'http://jyzx.scau.edu.cn/'),
    ('广东', '南方医科大学', 'http://fimmu.jysd.com/'),
    ('广东', '华南师范大学', 'http://career.scnu.edu.cn/'),
    ('广东', '广州大学', 'http://jy.gzhu.edu.cn/zpxj.htm'),
    ('广东', '广州外语外贸大学', 'https://career.gdufs.edu.cn/eweb/login.jsp'),
    ('广东', '韶关学院', 'http://job.sgu.edu.cn/index.aspx'),
    # 内蒙古
    ('内蒙古', '内蒙古大学', 'http://job.imu.edu.cn/'),
    ('内蒙古', '内蒙古科技大学', 'http://dadm.imust.cn/'),
    ('内蒙古', '内蒙古民族大学', 'http://imun.university-hr.cn/'),
    ('内蒙古', '内蒙古农业大学', 'https://job.imau.edu.cn/'),
    ('内蒙古', '内蒙古师范大学', 'http://jy.imnu.edu.cn/'),
    # 广西
    ('广西', '广西大学', 'http://zj.gxu.edu.cn/'),
    ('广西', '桂林电子科技大学', 'https://job.guet.edu.cn/'),
    ('广西', '广西师范大学', 'http://www.cg.gxnu.edu.cn/'),
    ('广西', '广西医科大学', 'http://jcy.gxmu.edu.cn/'),
    ('广西', '广西民族大学', 'https://jyb.gxun.edu.cn/'),
    ('广西', '桂林理工大学', 'https://glut.doerjob.com/'),
    ('广西', '桂林航天工业学院', 'http://bysjy.guat.edu.cn/'),
    # 海南
    ('海南', '海南大学', 'https://www.hainanu.edu.cn/jiuye/'),
    ('海南', '海南热带海洋学院', 'http://jyc.hntou.edu.cn/'),
    ('海南', '海南师范大学', 'http://jy.hainnu.edu.cn/unijob/index.php/web/Index/index'),
    ('海南', '海口经济学院', 'http://hkc.good-edu.cn/'),
    # 贵州
    ('贵州', '贵州大学', 'http://aoff.gzu.edu.cn/gzujobs/client/index'),
    ('贵州', '贵州师范大学', 'https://zjc.gznu.edu.cn:888/'),
    # 云南
    ('云南', '云南大学', 'http://jobs.ynu.edu.cn/'),
    ('云南', '昆明理工大学', 'http://job.kmust.edu.cn/'),
    ('云南', '云南农业大学', 'http://jyw.ynau.edu.cn/'),
    ('云南', '云南师范大学', 'http://job.ynnu.edu.cn/'),
    ('云南', '云南财经大学', 'http://jy.ynufe.edu.cn/'),
    ('云南', '云南民族大学', 'http://jyb.ynni.edu.cn/index'),
    ('云南', '云南林业大学', 'http://job.swfu.edu.cn/'),
    ('云南', '昆明医科大学', 'http://job.kmmc.cn/'),
    # 西藏
    ('西藏', '西藏大学', 'http://www.utibet.edu.cn/news/article_38_137_0.html'),
    # 陕西
    ('陕西', '长安大学', 'http://jyzx.chd.edu.cn/'),
    ('陕西', '西安交通大学', 'http://job.xjtu.edu.cn/'),
    ('陕西', '西安电子科技大学', 'https://job.xidian.edu.cn/'),
    ('陕西', '西北农林科技大学', 'https://job.nwsuaf.edu.cn/'),
    ('陕西', '陕西师范大学', 'http://job.snnu.edu.cn/'),
    ('陕西', '西北工业大学', 'http://job.nwpu.edu.cn/home.do'),
    ('陕西', '西北大学', 'http://jiuye.nwu.edu.cn/website/index.aspx'),
    ('陕西', '延安大学', 'http://yau.bysjy.com.cn/'),
    ('陕西', '西安理工大学', 'http://job.xaut.edu.cn/website/index.aspx'),
    ('陕西', '西安科技大学', 'http://jy.xust.edu.cn/website/index.aspx'),
    ('陕西', '西安石油大学', 'http://xsyu.bysjy.com.cn/'),
    ('陕西', '西安建筑科技大学', 'http://job.xauat.edu.cn/'),
    ('陕西', '西安工程大学', 'http://job.xpu.edu.cn/'),
    ('陕西', '陕西科技大学', 'http://jiuye.www.sust.edu.cn/'),
    ('陕西', '西安外国语大学', 'http://jiuye.xisu.edu.cn/'),
    ('陕西', '西安邮电大学', 'http://jiuye.xupt.edu.cn/'),
    ('陕西', '陕西理工大学', 'https://snut.cnxincai.com/schoolreception/index'),
    ('陕西', '西安财经大学', 'http://www.xaufejob.com/'),
    ('陕西', '西北政法大学', 'http://job.nwupl.edu.cn/'),
    # 甘肃
    ('甘肃', '兰州大学', 'https://job.lzu.edu.cn/'),
    ('甘肃', '西北民族大学', 'http://xbmu.bysjy.com.cn/index'),
    ('甘肃', '兰州交通大学', 'http://jyzx.lzjtu.edu.cn/eweb/jygl/index.so'),
    ('甘肃', '西北师范大学', 'https://grad.nwnu.edu.cn/'),
    ('甘肃', '兰州理工大学', 'http://jiuye.lut.cn/'),
    ('甘肃', '甘肃中医药大学', 'http://jyzd.gszy.edu.cn/Website/'),
    # 青海
    ('青海', '青海师范大学', 'https://jc.qhnu.edu.cn/'),
    ('青海', '青海大学', 'http://jyw.qhu.edu.cn/'),
    ('青海', '青海民族大学', 'http://qhmu.bysjy.com.cn/'),
    # 宁夏
    ('宁夏', '宁夏大学', 'https://www.nxujob.com/'),
    ('宁夏', '宁夏理工学院', 'http://www.nxist.com/NXLGJYW/views/index.form'),
    ('宁夏', '宁夏师范学院', 'http://jy.nxnu.edu.cn/'),
    # 新疆
    ('新疆', '新疆大学', 'http://job.xju.edu.cn/Web'),
    ('新疆', '石河子大学', 'http://scc.shzu.edu.cn/'),
]

# 连接数据库
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# 创建就业网站表
cursor.execute('''
CREATE TABLE IF NOT EXISTS career_websites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    province TEXT NOT NULL,
    school_name TEXT NOT NULL,
    website_url TEXT NOT NULL,
    source TEXT DEFAULT 'GitHub-PotoYang'
)
''')

# 插入数据
for province, school_name, website_url in career_websites:
    cursor.execute('''
        INSERT OR IGNORE INTO career_websites (province, school_name, website_url)
        VALUES (?, ?, ?)
    ''', (province, school_name, website_url))

conn.commit()

# 统计
cursor.execute("SELECT COUNT(*) FROM career_websites")
total = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(DISTINCT province) FROM career_websites")
province_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(DISTINCT school_name) FROM career_websites")
school_count = cursor.fetchone()[0]

print(f"就业网站数据库更新完成!")
print(f"总记录数: {total}")
print(f"涉及省份: {province_count}")
print(f"涉及高校: {school_count}")

# 按省份统计
print("\n各省份高校数量:")
cursor.execute("SELECT province, COUNT(*) FROM career_websites GROUP BY province ORDER BY COUNT(*) DESC")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]}所")

# 示例查询
print("\n示例数据 (浙江大学):")
cursor.execute("SELECT * FROM career_websites WHERE school_name = '浙江大学'")
for row in cursor.fetchall():
    print(f"  {row}")

conn.close()
print(f"\n数据库已更新: {db_file}")
