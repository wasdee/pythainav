# PythaiNAV

![cover image](https://github.com/CircleOnCircles/pythainav/raw/master/extra/pythainav.png)


ทำให้การดึงข้อมูลกองทุนไทยเป็นเรื่องง่าย

> อยากชวนทุกคนมาร่วมพัฒนา ติชม แนะนำ เพื่อให้ทุกคนเข้าถึงข้อมูลการง่ายขึ้น [เริ่มต้นได้ที่นี้](https://github.com/CircleOnCircles/pythainav/issues) หรือเข้ามา Chat ใน [Discord](https://discord.gg/jjuMcKZ) ได้เลย 😊

## Get Started - เริ่มต้นใช้งาน

```bash
$ pip install pythainav
```

```python
import pythainav as nav

nav.get("KT-PRECIOUS") 
> Nav(value=4.2696, updated='20/01/2020', tags={'latest'}, fund='KT-PRECIOUS')

nav.get("TISTECH-A") 
> Nav(value=12.9976, updated='21/01/2020', tags={'latest'}, fund='TISTECH-A')

```

## Source of Data - ที่มาข้อมูล

ตอนนี้ใช้ข้อมูลจาก website <https://www.finnomena.com/fund>

## Disclaimer 

เราไม่ได้เกี่ยวข้องกับ "finnomena.com" แต่อย่างใด เราไม่รับประกันความเสียหายใดๆทั้งสิ้นที่เกิดจาก แหล่งข้อมูล, library, source code,sample code, documentation, library dependencies และอื่นๆ