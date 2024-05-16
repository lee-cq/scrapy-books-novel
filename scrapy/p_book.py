#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@File Name  : p_book.py
@Author     : LeeCQ
@Date-Time  : 2023/5/12 20:23
"""

import re

html = '''
<ul>
<li>
<span class="s1"><b>类别</b></span>
<span class="s2"><b>小说</b></span>
<span class="s3"><b>最新</b></span>
<span class="s4"><b>作者</b></span>
<span class="s6"><b>时间</b></span>
<span class="s7"><b>状态</b></span>
</li>
<li>
<span class="s1">[奇魔玄幻]</span>
<span class="s2">
<a href="https://www.biququ.info/html/57569/" target="_blank">碧落天刀</a>
</span>
<span class="s3"><a href="https://www.biququ.info/html/57569/71961586.html" target="_blank">完本感言</a></span>
<span class="s4"><font color="red">风</font><font color="red">凌</font><font color="red">天</font><font color="red">下</font></span>
<span class="s6">2023-05-05</span>
<span class="s7"> 连载 </span>
</li>
<li>
<span class="s1">[奇魔玄幻]</span>
<span class="s2">
<a href="https://www.biququ.info/html/32877/" target="_blank">御道倾天</a>
</span>
<span class="s3"><a href="https://www.biququ.info/html/32877/410961472.html" target="_blank">新书《碧落天刀》已发。</a></span>
<span class="s4"><font color="red">风</font><font color="red">凌</font><font color="red">天</font><font color="red">下</font></span>
<span class="s6">2022-05-30</span>
<span class="s7"> 完本 </span>
</li>
<li>
<span class="s1">[奇魔玄幻]</span>
<span class="s2">
<a href="https://www.biququ.info/html/9814/" target="_blank">我是至尊</a>
</span>
<span class="s3"><a href="https://www.biququ.info/html/9814/122671499.html" target="_blank">完本感言+汇报（三）</a></span>
<span class="s4"><font color="red">风</font><font color="red">凌</font><font color="red">天</font><font color="red">下</font></span>
<span class="s6">2019-12-30</span>
<span class="s7"> 完本 </span>
</li>
<li>
<span class="s1">[奇魔玄幻]</span>
<span class="s2">
<a href="https://www.biququ.info/html/27794/" target="_blank">异世邪君</a>
</span>
<span class="s3"><a href="https://www.biququ.info/html/27794/347421276.html" target="_blank">大结局！</a></span>
<span class="s4"><font color="red">风</font><font color="red">凌</font><font color="red">天</font><font color="red">下</font></span>
<span class="s6">2019-09-07</span>
<span class="s7"> 完本 </span>
</li>
<li>
<span class="s1">[奇魔玄幻]</span>
<span class="s2">
<a href="https://www.biququ.info/html/36606/" target="_blank">凌天传说</a>
</span>
<span class="s3"><a href="https://www.biququ.info/html/36606/45757714.html" target="_blank">第七部 第九十六章 大结局（三）（全书完）</a></span>
<span class="s4"><font color="red">风</font><font color="red">凌</font><font color="red">天</font><font color="red">下</font></span>
<span class="s6">2019-08-10</span>
<span class="s7"> 完本 </span>
</li>
<li>
<span class="s1">[奇魔玄幻]</span>
<span class="s2">
<a href="https://www.biququ.info/html/6770/" target="_blank">天域苍穹</a>
</span>
<span class="s3"><a href="https://www.biququ.info/html/6770/84622379.html" target="_blank">完本感言:我很不满意!!!</a></span>
<span class="s4"><font color="red">风</font><font color="red">凌</font><font color="red">天</font><font color="red">下</font></span>
<span class="s6">2019-01-10</span>
<span class="s7"> 完本 </span>
</li>
</ul>
'''

a = re.findall(r'href="(.*?)/".*?>', html)
print(a)
