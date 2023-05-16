# **Python 太乙神數 Kintaiyi 堅太乙 年計 月計 日計 時計 分計**
[![Python](https://img.shields.io/pypi/pyversions/kintaiyi)](https://pypi.org/project/kintaiyi/)
[![PIP](https://img.shields.io/pypi/v/kintaiyi)](https://pypi.org/project/kintaiyi/)
[![Downloads](https://img.shields.io/pypi/dm/kintaiyi)](https://pypi.org/project/kintaiyi/)
[![TG Me](https://img.shields.io/badge/chat-on%20telegram-blue)](https://t.me/gnatnek)
[![TG Channel](https://img.shields.io/badge/chat-on%20telegram-red)](https://t.me/numerology_coding)
[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg?logo=paypal&style=flat-square)](https://www.paypal.me/kinyeah)&nbsp;


 ## 1. 導讀 Introduction
太乙神數是古代漢族占卜術的一種，與遁甲，六壬合稱三式，是推算天時以及歷史變化規律的術數學。周武王時以術數"卜世三十，卜年八百"推之，至邵雍形成歷史哲學而大備。據太乙神數推算，上古時有一年冬至日半夜，恰好日月合璧、五星連珠，定為甲子年、甲子月、甲子日、甲子時，稱作太極上元，上元甲子以來的年數，叫太乙積年。由太乙積年再求出太乙流年和太歲值卦，以斷本年各月的氣運凶吉，預測一些重大政治事件和天災人禍。採用五元六紀，三百六十年為一大周期，七十二年為一小周期，太乙每宮居三年，不入中宮，二十四年轉一周，七十二年遊三期。

太乙以一為太極生二目(主、客目)，二目生主客大小客與計神共八將。太乙乃天地之神，其星在太乙之前，統十六神而知風雨、水旱、兵革之事。昔黃帝與蚩尤大戰，適逢大霧，以霧書昏風後相，造指南車克之，是以取太乙之法，傳至今三千餘年，例目以為術數。外閱龍圖，內演龜文，凡天地之所以設君臣父子，之所以立陰陽，太乙了然演數則理昭著，太乙周行流運六十四卦，貴神入門十精之星，使經緯錯縮表理，集為一書。延續至今三千餘年不衰，為當今社會預測、決斷，提供了寶貴依據。

相傳太乙式產生于黃帝戰蚩尤時。其法大扺本于《易緯.乾鑿度》太乙行九宮法。採用五元六紀，三百六十年為一大周期，七十二年為一小周期，太乙每宮居三年，不入中宮，二十四年轉一周，七十二年遊三期。太乙以一為太極生二目(主、客目)，二目生主客大小客與計神共八將。(與易經太極分二儀，二儀生四象，四象生八卦相仿)。以太乙八將所乘十六神之方位關系定出格局。可佔內外祝福。又臨四時之分野，可佔水旱疾疫。再推三基五福大小遊二限，可預測古今治亂。又可推出年卦、月卦等。

因應現代都市人的需求，與時並進，就時計太乙的基礎上，下開分計太乙，至於果效，留待閣下驗證。

Tai Yi Shen Shu is a form of divination from China. It is also one of the Three Styles (三式; sānshì; 'three styles') of divination, the others being Da Liu Ren and Qi Men Dun Jia. Tai Yi Shen Shu is used to predict macroscopic events like wars or the meaning of supernovae. One form of Tai Yi Shen Shu has been popularized over the centuries to predict personal fortunes. Genghis Khan, emperor of China, referred to Tai Yi at one point to decide whether or not his planned invasion of Japan would succeed. When the Tai Yi count indicated that invasion would prove unsuccessful, Khan decided not to invade Japan that year. Numerous similar examples abound in classical Chinese literature, especially among the dynastic histories.

The methodology is quite similar to the other arts with a rotating heavenly plate and fixed earthly plate. While the art makes use of the 8 trigrams as well as the 64 hexagrams as a foundation, analysis is conducted from the Tai Yi Cosmic Board and the array of symbols found thereon, with special reference to the position of symbols in specific palaces. Important symbols include the Calculator, the Scholar, Tai Yi and Tai Yi, for example.

A number of spirits rotate around the sixteen palaces of the Tai Yi cosmic board, of which there are 72 cosmic boards for the Yin Dun period of each year, and 72 cosmic boards for the Yang Dun period of the year. The spirits land in different palaces with each configuration of the cosmic board. Each cosmic board contains a number of "counts" or numbers – the Host Count and the Guest Count taking primary importance over the Fixed Count.

含史事對照的太鳦排盤 https://kintaiyi.streamlitapp.com

Taiyishenshu, one of the Ancient Chinese Divinations, along with Qimendunjia and Dailiuren known as "three styles".


## 2. 安裝套件 Installation
```python
	pip install kintaiyi
	pip install --upgrade sxtwl, numpy, ephem, cn2an 
```
## 3. 起課方式 Quickstart
```python
	from kintaiyi import kintaiyi
	# 0 為年計；1 為月計；2 為日計：3 為時計；4 為分計
	#公元前
	Taiyi(-202,9,16,23,14).pan(1)
	{'太乙計': '月計', '公元日期': '-202年9月16日23時', '干支': ['戊戌', '辛酉', '庚戌', '丙子'], '農曆': {'年': -202, '月': 8, '日': 15}, '年號': '西漢高帝劉邦 高帝四年', '紀元': '第三紀第一甲子元', '時局': {'文': '陽遁十局', '數': 10}, '太乙': 4, '文昌': '丑', '太歲': '子', '合神': '丑', '計神': '寅', '始擊': '子', '定目': '子', '主算': [4, ['無天', '無地', '雜陽']], '客算': [11, ['無地', '陰中重陽']], '定算': [11, ['無地', '陰中重陽']], '九宮': {8: '大游', 3: '客參定參', 4: '主將太乙', 9: '', 5: '五風', 2: '主參八風', 7: '三風', 6: '', 1: '客將定將飛鳥小游'}, '十六宮': {'子': ['太歲', '始擊', '定目'], '丑': ['文昌', '合神', '四神'], '艮': [], '寅': [], '卯': [], '辰': ['君基'], '巽': ['五福'], '巳': ['民基'], '午': ['飛符', '太尊'], '未': ['臣基', '地乙'], '申': [], '坤': [], '酉': [], '戌': ['直符'], '乾': ['帝符'], '亥': ['天乙']}}
	#公元
	Taiyi(658,5,31,0,14).pan(0) 
	{'太乙計': '時計', '公元日期': '658年5月31日0時', '干支': ['戊午', '丁巳', '丙子', '戊子'], '農曆': {'年': 658, '月': 4, '日': 24}, '年號': '唐高宗李治 永徽九年', '紀元': '丙子元第二紀', '時局': '陽遁37局', '太乙': 6, '文昌': '坤', '太歲': '子', '合神': '丑', '計神': '寅', '始擊': '未', '定目': '未', '主算': [7, ['無天', '雜陰']], '客算': [8, ['無天', '雜陽']], '定算': [8, ['無天', '雜陽']], '九宮': {8: '客將定將大游', 3: '五風', 4: '客參定參', 9: '', 5: '', 2: '八風', 7: '主將三風', 6: '太乙', 1: '主參飛鳥小游'}, '十六宮': {'子': ['太歲', '太尊'], '丑': ['合神'], '艮': [], '寅': [], '卯': [], '辰': ['君基', '臣基', '帝符'], '巽': [], '巳': [], '午': [], '未': ['始擊', '定目'], '申': ['民基'], '坤': ['文昌'], '酉': [], '戌': [], '乾': ['五福'], '亥': []}}
	
```
